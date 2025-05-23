import re
import pandas as pd

filename = "chat.txt"
excel_output = "parsed_chat_data.xlsx"
text_output_orders = "orders_only.txt"
text_output_all = "all_messages.txt"

order_keywords = ["заказ №", "имя", "номер"]

msg_pattern = re.compile(r'^(\d{2}\.\d{2}\.\d{4}), (\d{2}:\d{2}) - (.*?): (.*)')
phone_pattern = re.compile(r'(\+7[\d\s\-]{10,15}|\b87\d{9}\b)')

messages = []
current = {"date": None, "time": None, "name": None, "text": "", "phone": "", "is_order": False}

def check_if_order(text):
    return any(word.lower() in text.lower() for word in order_keywords)

with open(filename, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        match = msg_pattern.match(line)
        if match:
            if current["text"]:
                current["is_order"] = check_if_order(current["text"])
                messages.append(current.copy())
                current["text"] = ""

            current["date"] = match.group(1)
            current["time"] = match.group(2)
            current["name"] = match.group(3)
            current["text"] = match.group(4)

            combined_text = match.group(3) + " " + match.group(4)
            phone_match = phone_pattern.search(combined_text)
            current["phone"] = phone_match.group(1) if phone_match else ""
        else:
            current["text"] += " " + line
            if not current["phone"]:
                phone_match = phone_pattern.search(line)
                if phone_match:
                    current["phone"] = phone_match.group(1)

if current["text"]:
    current["is_order"] = check_if_order(current["text"])
    messages.append(current.copy())

# Create DataFrame
df = pd.DataFrame(messages)
df.rename(columns={
    "date": "Date",
    "time": "Time",
    "name": "Sender",
    "phone": "Phone Number",
    "text": "Message",
    "is_order": "IsOrder"
}, inplace=True)

# Filter only orders
df_orders = df[df["IsOrder"] == True]

# Save only orders to Excel
df_orders.to_excel(excel_output, index=False)

# Save text outputs
with open(text_output_all, 'w', encoding='utf-8') as all_file, \
     open(text_output_orders, 'w', encoding='utf-8') as order_file:

    for idx, row in df.iterrows():
        line = f"[{row['Date']} {row['Time']}] {row['Sender']} ({row['Phone Number']}): {row['Message']}\n\n"
        all_file.write(line)
        if row["IsOrder"]:
            order_file.write(line)

print(f"Orders have been filtered and saved to {excel_output}")
