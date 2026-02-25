⚖️ My AI Model Failed 3 Times Before It Learned to Simplify Legal Jargon. Here's the Full Story.

I fine-tuned an LLM to translate legal contracts into plain English.

It broke 3 times before it worked. Here's the real journey 👇

— — —

𝗙𝗮𝗶𝗹𝘂𝗿𝗲 #𝟭: 𝗧𝗵𝗲 𝗗𝗮𝘁𝗮 𝗧𝗿𝗮𝗽

Started with the CUAD dataset (510+ real SEC-filed contracts). But CUAD only has complex clauses — no simplified versions.

So I built a script to generate parallel training data. Got 110 pairs. But 90% of the targets defaulted to the same generic placeholder. I didn't realize it yet.

𝗙𝗮𝗶𝗹𝘂𝗿𝗲 #𝟮: 𝗡𝗮𝗡 𝗟𝗼𝘀𝘀𝗲𝘀 & 𝗠𝗼𝗱𝗲 𝗖𝗼𝗹𝗹𝗮𝗽𝘀𝗲

Picked FLAN-T5 + LoRA. Enabled fp16.

Training Loss: 0.000000 | Validation Loss: NaN

T5 is unstable in 16-bit precision. Fixed that. Retrained on Colab.

New output for EVERY input: "This clause applies only to the parties."

Mode collapse. The model memorized the one repeated placeholder from my dataset.

𝗙𝗮𝗶𝗹𝘂𝗿𝗲 #𝟯: 𝗕𝗲𝘁𝘁𝗲𝗿 𝗗𝗮𝘁𝗮, 𝗦𝘁𝗶𝗹𝗹 𝗕𝗿𝗼𝗸𝗲𝗻

Rebuilt the dataset — 2,000 unique pairs across 8+ legal categories.

FLAN-T5 output: "The failure a legal problem in a legal problem."

Gibberish. The Seq2Seq architecture + aggressive learning rate destroyed the model's language ability.

— — —

𝗧𝗵𝗲 𝗣𝗶𝘃𝗼𝘁 𝗧𝗵𝗮𝘁 𝗖𝗵𝗮𝗻𝗴𝗲𝗱 𝗘𝘃𝗲𝗿𝘆𝘁𝗵𝗶𝗻𝗴

Switched to Google's Gemma-2B with a completely different strategy:

→ QLoRA (4-bit quantization) — 2.5B params on a free Colab T4
→ Only 921,600 trainable params (0.037% of total)
→ SFTTrainer from TRL with Gemma's chat template

Training loss: 3.58 → 0.77 in 25 minutes.

Input: "In witness whereof, the parties hereto have executed this Agreement..."
Output: "The parties mentioned in this clause have done everything that is in the next clause."

It worked. Not a placeholder. Not gibberish. A real simplification.

— — —

𝗞𝗲𝘆 𝗟𝗲𝘀𝘀𝗼𝗻𝘀:

1. Data quality > quantity. 2,000 curated pairs beat 10,000 generic ones.
2. Architecture matters. FLAN-T5 failed. Gemma-2B nailed it.
3. QLoRA democratizes fine-tuning. 2.5B params on a free GPU is real.
4. ML debugging is an engineering skill. NaN, mode collapse, gibberish — each taught me more than any course.

𝗧𝗲𝗰𝗵 𝗦𝘁𝗮𝗰𝗸: Python · HuggingFace · PEFT/LoRA · TRL · bitsandbytes · Colab T4

Open-source on GitHub (link in comments).

♻️ Repost if you believe AI should make legal documents accessible to everyone.

#AI #MachineLearning #LLM #NLP #Gemma #HuggingFace #LegalTech #QLoRA #BuildInPublic #OpenSource
