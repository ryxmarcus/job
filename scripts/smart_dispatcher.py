"""Smart Resume & Track Dispatcher for Rahul Kumar's Job Pipeline."""
import json
import re

TRACK_CRITERIA = {
    "SRE": {
        "keywords": ["sre", "site reliability", "reliability engineer", "prometheus", "grafana", "observability", "incident", "slo", "sli", "istio"],
        "recommended_resume": "Rahul_Kumar_Site_Reliability_Engineer_CV.pdf",
        "focus_headline": "Site Reliability Engineer (SRE) | AWS Certified DevOps Pro | Kubernetes, Linux, Prometheus, Grafana"
    },
    "DevOps_AWS": {
        "keywords": ["devops", "aws", "cloud engineer", "terraform", "eks", "jenkins", "argocd", "ci/cd", "iac", "docker"],
        "recommended_resume": "Rahul_Kumar_DevOps_AWS_2026.pdf",
        "focus_headline": "AWS Certified DevOps Pro (DOP-C02) | EKS, Terraform, ArgoCD, Python, Linux | 30 Days Notice"
    },
    "MLOps_Platform": {
        "keywords": ["mlops", "ai platform", "kubeflow", "mlflow", "data engineer", "etl", "machine learning engineer"],
        "recommended_resume": "Rahul_Kumar_MLOps_Engineer_CV.pdf",
        "focus_headline": "MLOps & Cloud Platform Engineer | Kubernetes, Kubeflow, MLflow, AWS EKS, Python"
    },
    "Forward_Deployed": {
        "keywords": ["forward deployed", "solutions engineer", "technical client", "enterprise architect", "fde"],
        "recommended_resume": "Rahul_Kumar_Forward_Deployed_Engineer_CV.pdf",
        "focus_headline": "Forward Deployed Engineer (FDE) | Cloud Architecture, Python, AWS, Enterprise Client Delivery"
    }
}

def classify_job(title: str, description: str = "") -> dict:
    text = (title + " " + description).lower()
    best_track = "DevOps_AWS"
    highest_score = 0
    
    for track, data in TRACK_CRITERIA.items():
        score = sum(1 for kw in data["keywords"] if kw in text)
        if score > highest_score:
            highest_score = score
            best_track = track
            
    return {
        "track": best_track,
        "score": highest_score,
        "resume": TRACK_CRITERIA[best_track]["recommended_resume"],
        "headline": TRACK_CRITERIA[best_track]["focus_headline"]
    }

if __name__ == "__main__":
    test_roles = [
        "Site Reliability Engineer III - Observability",
        "AWS Cloud Platform & DevOps Engineer",
        "MLOps Engineer - Generative AI Infrastructure",
        "Forward Deployed Engineer - Industry Solutions"
    ]
    for r in test_roles:
        res = classify_job(r)
        print(f"Role: {r}")
        print(f"  -> Track: {res['track']} | Resume: {res['resume']}")

