import tkinter as tk
from tkinter import ttk

DROPDOWN_WIDTH = 30


def create_speaker_dropdown(root, speaker_choices, width=DROPDOWN_WIDTH):
    tk.Label(root, text="ボイス選択").pack()
    speaker_var = tk.StringVar()
    speaker_dropdown = ttk.Combobox(root, textvariable=speaker_var, width=width)
    speaker_dropdown["values"] = speaker_choices
    if speaker_choices:
        speaker_dropdown.current(0)
    speaker_dropdown.pack()
    return speaker_dropdown, speaker_var


def create_model_dropdown(root, models, width=DROPDOWN_WIDTH):
    tk.Label(root, text="モデル選択").pack()
    model_var = tk.StringVar()
    model_combobox = ttk.Combobox(
        root, textvariable=model_var, state="readonly", width=width
    )
    model_combobox.pack()
    if models:
        model_combobox["values"] = models
        model_combobox.current(0)
    else:
        model_combobox["values"] = ["(取得失敗)"]
        model_combobox.current(0)
    return model_combobox, model_var
