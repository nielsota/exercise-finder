from exercise_finder.enums import AgentName, OpenAIModel

agent_name_to_model_mapping = {
    AgentName.IMAGES_TO_QUESTION_AGENT: OpenAIModel.GPT_4O,
    AgentName.FORMAT_MULTIPART_QUESTION_AGENT: OpenAIModel.GPT_5_MINI,
}
