import nltk
import matplotlib.pyplot as plt
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

# Download NLTK resources
nltk.download("punkt")


# Helper function to evaluate translation
def evaluate_translation(translated_text, target_text):
    translated_tokens = nltk.word_tokenize(translated_text)
    target_tokens = nltk.word_tokenize(target_text)

    # BLEU (precision-based metric)
    smooth_func = SmoothingFunction().method4
    bleu = sentence_bleu(
        [target_tokens], translated_tokens, smoothing_function=smooth_func
    )

    # ROUGE (recall/overlap-based metrics)
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    rouge = scorer.score(target_text, translated_text)

    return {
        "BLEU": bleu,
        "ROUGE-1": rouge["rouge1"].fmeasure,
        "ROUGE-2": rouge["rouge2"].fmeasure,
        "ROUGE-L": rouge["rougeL"].fmeasure,
    }


# Read target text
with open("target_bahasa.txt", "r", encoding="utf-8") as f:
    target_text = f.read()

# Read translation files
with open("translated_azure.txt", "r", encoding="utf-8") as f:
    translated_azure = f.read()

with open("translated_deepL.txt", "r", encoding="utf-8") as f:
    translated_deepl = f.read()

# Evaluate translations
azure_scores = evaluate_translation(translated_azure, target_text)
deepl_scores = evaluate_translation(translated_deepl, target_text)

# Prepare for plotting
metrics = ["BLEU", "ROUGE-1", "ROUGE-2", "ROUGE-L"]
azure_values = [azure_scores[m] for m in metrics]
deepl_values = [deepl_scores[m] for m in metrics]

x = range(len(metrics))
width = 0.35

# Plotting
plt.figure(figsize=(12, 7))
azure_bars = plt.bar(
    [i - width / 2 for i in x],
    azure_values,
    width=width,
    label="Azure",
    color="skyblue",
)
deepl_bars = plt.bar(
    [i + width / 2 for i in x], deepl_values, width=width, label="DeepL", color="salmon"
)

# Title and labels
plt.xlabel("Evaluation Metrics")
plt.ylabel("Score")
plt.title("Translation Evaluation Metrics Comparison: Azure vs DeepL")
plt.xticks(x, metrics)
plt.ylim(0, 1)

# Annotate scores on bars
for i in x:
    plt.text(
        i - width / 2, azure_values[i] + 0.02, f"{azure_values[i]:.4f}", ha="center"
    )
    plt.text(
        i + width / 2, deepl_values[i] + 0.02, f"{deepl_values[i]:.4f}", ha="center"
    )

# Custom legend explanation
custom_lines = [
    plt.Line2D([0], [0], color="skyblue", lw=10),
    plt.Line2D([0], [0], color="salmon", lw=10),
    plt.Line2D([0], [0], color="black", lw=0, label=""),
    plt.Line2D(
        [0],
        [0],
        color="white",
        marker="o",
        label="BLEU = Precision-based (how much predicted overlaps with reference)",
    ),
    plt.Line2D(
        [0],
        [0],
        color="white",
        marker="o",
        label="ROUGE = Recall-based (how much reference is covered by prediction)",
    ),
]

plt.legend(
    custom_lines[:2] + custom_lines[3:],
    [
        "Azure Translation",
        "DeepL Translation",
        "BLEU → Precision-based (predicted overlap)",
        "ROUGE → Recall-based (reference coverage)",
    ],
    loc="lower center",
    bbox_to_anchor=(0.5, -0.25),
    fontsize="medium",
    frameon=False,
)

plt.tight_layout()
plt.savefig("perbandingan_evaluasi_dengan_keterangan.png")
plt.show()
