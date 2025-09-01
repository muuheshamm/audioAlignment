import os
import json
import re
import soundfile as sf

# ========== Config ==========
audio_path = "0005.wav"   
transcript_path = "transcript05.txt"
alignment_json_path = "precise_alignment05.json"

output_dir = "glassroom03"
os.makedirs(output_dir, exist_ok=True)

# Start numbering here (
start_counter = 1559

# Padding 
padding = 0.15
# ============================

# --- Robust transcript loader with fallback encodings ---
def load_transcript(path):
    encodings_to_try = ['utf-8', 'cp1256', 'iso-8859-6', 'latin1']
    for enc in encodings_to_try:
        try:
            with open(path, 'r', encoding=enc) as f:
                lines = [line.strip() for line in f if line.strip()]
            print(f"Loaded transcript with encoding: {enc}")
            return lines
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("utf-8", b"", 0, 1, f"Failed to decode transcript with tried encodings: {encodings_to_try}")

sentences = load_transcript(transcript_path)

# --- Load alignment JSON ---
with open(alignment_json_path, 'r', encoding='utf-8') as f:
    alignment_data = json.load(f)
word_timestamps = alignment_data["word_timestamps"]

# --- Arabic normalization helpers (for reliable matching) ---
AR_DIACRITICS_RE = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
PUNCTUATION = '.,!?;:،؛؟«»"\'()[]{}<>…ـ'

def normalize_ar(text: str) -> str:
    t = text.strip()
    t = AR_DIACRITICS_RE.sub('', t)  # remove diacritics
    t = (t.replace('أ', 'ا')
           .replace('إ', 'ا')
           .replace('آ', 'ا')
           .replace('ٱ', 'ا')
           .replace('ؤ', 'و')
           .replace('ئ', 'ي')
           .replace('ى', 'ي')
           .replace('ـ', ''))
    t = t.replace('ة', 'ه')
    t = t.translate(str.maketrans('', '', PUNCTUATION + ' '))
    return t

# --- Build precise sentence spans by consuming ASR words ---
def group_word_timestamps_by_sentence(sentences, word_timestamps):
    grouped = []
    word_idx = 0
    num_words = len(word_timestamps)

    for sent in sentences:
        target = normalize_ar(sent)
        concat = ""
        collected = []
        start_time = None
        end_time = None

        while word_idx < num_words and len(concat) < len(target):
            w = word_timestamps[word_idx]
            w_norm = normalize_ar(w["text"])
            concat += w_norm
            if start_time is None:
                start_time = w["start"]
            end_time = w["end"]
            collected.append(w)
            word_idx += 1

            if not target.startswith(concat):
                word_idx -= 1
                collected.pop()
                if collected:
                    end_time = collected[-1]["end"]
                break

        grouped.append({
            "sentence": sent,
            "start": start_time,
            "end": end_time,
            "words": collected,
        })

    return grouped

sentence_spans = group_word_timestamps_by_sentence(sentences, word_timestamps)

# --- Combine into chunks: 4 sentences per chunk; if odd total, last 5 ---
def combine_sentences(spans):
    combined = []
    i = 0
    n = len(spans)
    while i < n:
        remain = n - i
        if remain == 5:  
            chunk_spans = spans[i:i+5]
            i += 5
        else:  
            chunk_spans = spans[i:i+4]
            i += 4

        start_time = chunk_spans[0]["start"]
        end_time = chunk_spans[-1]["end"]

        combined_sentence = "\n".join(s["sentence"] for s in chunk_spans)

        words_flat = []
        for s in chunk_spans:
            words_flat.extend(s["words"])

        combined.append({
            "sentence": combined_sentence,
            "start": start_time,
            "end": end_time,
            "words": words_flat
        })
    return combined

combined_spans = combine_sentences(sentence_spans)

# --- Load audio and write chunks ---
audio, sr = sf.read(audio_path)

def write_chunk(base_idx, span, out_dir):
    if span["start"] is None or span["end"] is None:
        print(f"Skipping chunk_{base_idx:02d}: missing timestamps")
        return False

    start_sample = max(0, int((span["start"]) * sr))
    end_sample = min(len(audio), int((span["end"] + padding) * sr))

    if end_sample <= start_sample:
        print(f"Skipping chunk_{base_idx:02d}: empty or invalid range ({start_sample}, {end_sample})")
        return False

    base_name = f"chunk_{base_idx:02d}"
    out_audio_path = os.path.join(out_dir, f"{base_name}.wav")
    out_text_path = os.path.join(out_dir, f"{base_name}.txt")

    sf.write(out_audio_path, audio[start_sample:end_sample], sr)
    with open(out_text_path, "w", encoding="utf-8") as f:
        f.write(span["sentence"])

    print(f"Saved {base_name} -> {out_audio_path}  |  {out_text_path}")
    return True

written = 0
for i, span in enumerate(combined_spans, start=start_counter):
    if write_chunk(i, span, output_dir):
        written += 1

print(f"\nDone. Wrote {written} chunk(s) into: {output_dir}")
