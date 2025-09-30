import os
os.environ["TRANSFORMERS_NO_TF"] = "1" 

import torch
from transformers import BertTokenizer, BertForSequenceClassification

MODEL_DIR = r"D:\summer2025\Digitopea\DIGITOPIA\backend\crime_report_system\reports\final_trained_model_severity"

tokenizer = BertTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
model = BertForSequenceClassification.from_pretrained(MODEL_DIR, local_files_only=True)

def predict_severity(text: str) -> str:
    """يتوقع مستوى الخطورة للنص"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        predicted_class_id = outputs.logits.argmax().item()
    return model.config.id2label[predicted_class_id]


# ------------------------------------------------------------------------------------------------------------

# from reports.models import Report
# from reports.ml_model import predict_severity

# # جلب كل البلاغات اللي severity فاضية
# reports = Report.objects.filter(severity__isnull=True)

# for report in reports:
#     text = report.report_details 
#     severity_pred = predict_severity(text) 
#     report.severity = severity_pred
#     report.save(update_fields=["severity"])

# print(f"✅ Done! Updated {reports.count()} reports with predicted severity.")
