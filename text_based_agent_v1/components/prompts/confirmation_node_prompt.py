from langchain_core.prompts import ChatPromptTemplate,SystemMessagePromptTemplate, HumanMessagePromptTemplate


CONFIRMATION_NODE_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are an AI assistant helping to confirm user-provided answers to some questions."
    ),
    HumanMessagePromptTemplate.from_template(
        """
        The list of questions and answers is as follows:
        {questions_and_answers}
        ---------------------------------------------------------------------
        """
    )
])