import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
from openpyxl.workbook import Workbook


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

headers       = ['Query','Responses']
workbook_name = 'sample.xlsx'
wb = Workbook()
page = wb.active
page.title = 'Results'
page.append(headers) # write the headers to the first line

bot_name = "Desti"

def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                response = random.choice(intent['responses'])
                page.append([msg, response])
                return response
    page.append([msg, "Message Unrecognized"])
    return "I do not understand..."


if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        # sentence = "do you use credit cards?"
        print(bot_name + ": What climate do you like?")
        climate = input("You: ")
        print(bot_name + ": What type of destination are you looking for?")
        destination = input("You: ")
        print(bot_name + ": Which continent would you ideally like to visit?")
        continent = input("You: ")
        sentence = (climate+" " + destination + " "+ continent)
        if "quit" in sentence:
            break
        resp = get_response(sentence)
        print(resp)
    wb.save(filename = workbook_name)