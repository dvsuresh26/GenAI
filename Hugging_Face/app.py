import streamlit as st
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModel,pipeline
import torch
import faiss
from langchain.vectorstores import FAISS
import pickle
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

st.title("News Research 🔬 ")

st.sidebar.title("News articles URLs Below")

def generate_embeddings(texts, tokenizer, model):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        #   outputs = model(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'])

    return outputs.last_hidden_state.mean(dim=1).numpy()

def search_faiss_index(query, tokenizer, model, index, text_chunks, k=2):
    query_embedding = generate_embeddings([query], tokenizer, model)
    D, I = index.search(query_embedding, k)
    return [text_chunks[idx] for idx in I[0]]

def answer_question(question, retrieved_docs, qa_model):
    answers = []
    for doc in retrieved_docs:
        result = qa_model(question=question, context=doc)
        top_answer = result['answer']
        answers.append(top_answer)
    return answers

urls=[]
for i in range(2):
    url=st.sidebar.text_input(f"URL{i+1}")
    urls.append(url)

process_url_clicked = st.sidebar.button("Research")
main_status=st.empty();
if(process_url_clicked):
    #load data
    loader = UnstructuredURLLoader(urls)
    main_status.text("Data Loading Started ✅")
    data = loader.load()
    main_status.text("Text Splitter ✅")
    #split data
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    )
    docs=text_splitter.split_documents(data)
    flattended_chunks = [chunk.page_content for chunk in docs]

    #Create tokens and Embeddings
    main_status.text("Tokenization Started ✅")
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    main_status.text("Embeddings Started ✅")
    embeddings = generate_embeddings(flattended_chunks,tokenizer,model)
    #Saving into FAISS
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    main_status.text("Embeddings saved to FAISS ✅")
    with open('faiss_index.pkl', 'wb') as f:
        pickle.dump((flattended_chunks, embeddings, index), f)

query = main_status.text_input("Your Question")
if(query):
    with open('faiss_index.pkl', 'rb') as f:
        flattended_chunks, embeddings, index = pickle.load(f)
    # query_embedding = generate_embeddings([query], tokenizer, model)
    # D, I = index.search(query_embedding, k=2)
    qa_model_name = 'deepset/roberta-base-squad2'  # Example QA model
    qa_tokenizer = AutoTokenizer.from_pretrained(qa_model_name)
    qa_model = pipeline('question-answering', model=qa_model_name, tokenizer=qa_tokenizer)
    # retrieved_docs = search_faiss_index(query, qa_tokenizer, qa_model, index, flattended_chunks)
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    retrieved_docs = search_faiss_index(query, tokenizer, model, index, flattended_chunks)

    answers = answer_question(query, retrieved_docs, qa_model)
    st.header("Answer")
    st.subheader(answers)