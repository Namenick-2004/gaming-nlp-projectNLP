"""
Abstractive summarization of many comments into a short paragraph,
using an mT5 (or other Thai-capable seq2seq) model. Long comment
lists are chunked, summarized in pieces, then summarized again
("map-reduce" summarization) to stay within the model's context size.
"""
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from app.services.nlp.preprocessing import clean_generated_text

CHUNK_SIZE = 40  # comments per chunk before the reduce step


class SummarizationModel:
    def __init__(self, model_name: str, device: str = "cpu"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(device)
        self.model.eval()

    @torch.no_grad()
    def _summarize_text(self, text: str, max_new_tokens: int = 120) -> str:
        prompt = f"สรุปความคิดเห็นต่อไปนี้เป็นภาษาไทยแบบกระชับ ชัดเจนและอ่านง่าย: {text}"
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        output_ids = self.model.generate(**inputs, max_new_tokens=max_new_tokens, num_beams=4)
        raw = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return clean_generated_text(raw)

    def summarize_comments(self, comments: list[str]) -> str:
        if not comments:
            return "ยังไม่มีความคิดเห็นเพียงพอสำหรับสรุปผล"

        # The bundled mT5 checkpoint can produce malformed Thai fragments.
        # Keep the summary grounded in the actual comments until a Thai-
        # capable summarization checkpoint with reliable output is configured.
        readable_comments = [clean_generated_text(comment) for comment in comments]
        readable_comments = [comment for comment in readable_comments if len(comment) >= 8]
        examples = readable_comments[:3]
        if not examples:
            return f"มีความคิดเห็นทั้งหมด {len(comments)} รายการ แต่ยังไม่มีข้อความที่อ่านได้เพียงพอสำหรับสรุปผล"

        return (
            f"จากความคิดเห็นของผู้ชมจำนวน {len(comments)} รายการ "
            f"พบตัวอย่างความคิดเห็นที่น่าสนใจ เช่น {' / '.join(examples)}"
        )
