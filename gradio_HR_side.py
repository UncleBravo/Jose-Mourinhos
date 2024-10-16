import gradio as gr
import pandas as pd

def format_data():
    with open("applicants.txt", "r") as applicant_file:
        lines = applicant_file.readlines()
        data = {
            "Name": [],
            "Role": [],
            "Field of Role": [],
            "Final Percentage Score": [],
            "Recommended Role": []
        }

        for line in lines:
            name, role, field, percentage, recommended_role = line.strip().split(", ")
            data["Name"].append(name)
            data["Role"].append(role)
            data["Field of Role"].append(field)
            data["Final Percentage Score"].append(percentage)
            data["Recommended Role"].append(recommended_role)
    
    return pd.DataFrame(data)

def filer(role):
    df = format_data()
    if role != "All":
        return df[df["Field of Role"] == role]
    return df

demo1 = gr.Blocks()

with demo1:
    role = gr.Dropdown(["All", "Business", "Finance", "Computing", "HR"], value="All", label="Field")
    output = gr.DataFrame(filer, inputs=[role])

demo1.launch()