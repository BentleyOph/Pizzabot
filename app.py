import openai
import streamlit as st
import time
import os
import json
from database_connectivity import InsertOrderDetails, FindCustomer
from dotenv import load_dotenv
load_dotenv() 



def place_order(pizza_size, pizza_flavor,customer_name, customer_address, customer_phone,pizza_toppings=None, pizza_extras=None):
    order_details = f"Pizza Size: {pizza_size}\nPizza Flavor: {pizza_flavor}\n"
    if pizza_toppings:
        order_details += f"Toppings: {pizza_toppings}\n"
    if pizza_extras:
        order_details += f"Extras: {pizza_extras}\n"
    customer_details = f"Customer Name: {customer_name}\nCustomer Address: {customer_address}\nCustomer Phone: {customer_phone}\n"
    InsertOrderDetails(pizza_flavor, pizza_size, "15209")

def handle_function(run):
    tools_to_call = run.required_action.submit_tool_outputs.tool_calls
    tools_output_array = []
    for each_tool in tools_to_call:
        tool_call_id = each_tool.id
        function_name = each_tool.function.name
        function_arg = each_tool.function.arguments
        print("Tool ID:" + tool_call_id)
        print("Function to Call:" + function_name )
        print("Parameters to use:" + function_arg)

        if (function_name == 'place_order'):
            arguments_str = each_tool.function.arguments
            arguments_dict = json.loads(arguments_str)
            pizza_size = arguments_dict['pizza_size']
            pizza_flavor = arguments_dict['pizza_flavor']
            pizza_toppings = arguments_dict.get('pizza_toppings', None)
            pizza_extras = arguments_dict.get('pizza_extras', None)
            customer_name = arguments_dict['customer_name']
            customer_address = arguments_dict['customer_address']
            customer_phone = arguments_dict['customer_phone']
            place_order(pizza_size, pizza_flavor,customer_name, customer_address, customer_phone,pizza_toppings, pizza_extras)
            output = "Say the order has been placed.Try to provide the total amount of each item to be paid.Also say Just pay the delivery guy when he arrives or pay online at our website.Make sure to provide any available promos or discounts if any.Also ask if they would like to add anything else to their order."
            tools_output_array.append({"tool_call_id": tool_call_id, "output": output})

    client.beta.threads.runs.submit_tool_outputs(
        thread_id = st.session_state.thread_id,
        run_id = run.id,
        tool_outputs=tools_output_array
    )   

#set assistant id
assistant_id = os.getenv("ASSISTANT_ID")

#initializa openai client
client = openai

#initialize session state variables for file IDs and chat control 
if 'file_id' not in st.session_state:
    st.session_state.file_id_list = []
if 'start_chat' not in st.session_state:
    st.session_state.start_chat = False
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None

#setup the streamlit page with a title and description
st.set_page_config(page_title="Pizza Inn", page_icon=":robot_face:", layout="wide")
st.header(":pizza: Pizza Inn")

openai_api_key_env = os.getenv('OPENAI_API_KEY')
openai_api_key = st.sidebar.text_input(
    'OpenAI API Key', placeholder='sk-', value=openai_api_key_env)
url = "https://platform.openai.com/account/api-keys"
st.sidebar.markdown("Get an Open AI Access Key [here](%s). " % url)
if openai_api_key:
    openai.api_key = openai_api_key

# Button to start the chat session
if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    # Create a thread once and store its ID in session state
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.write("thread id: ", thread.id)

# Define the function to process messages with citations
def process_message_with_citations(message):
    message_content = message.content[0].text.value
    return message_content

# Only show the chat interface if the chat has been started
if st.session_state.start_chat:
   # st.write(getStockPrice('AAPL'))
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for the user
    if prompt := st.chat_input("How can I help you?"):
        # Add user message to the state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add the user's message to the existing thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Create a run with additional instructions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            #instructions="Please answer the queries using the knowledge provided in the files.When adding other information mark it clearly as such.with a different color"
        )

        # Poll for the run to complete and retrieve the assistant's messages
        while run.status not in ["completed", "failed"]:
            st.sidebar.write(run.status)
            if run.status == "requires_action":
                handle_function(run)
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        st.sidebar.write(run.status)

        # Retrieve messages added by the assistant
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            full_response = process_message_with_citations(message)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            with st.chat_message("assistant"):
                st.markdown(full_response, unsafe_allow_html=True)