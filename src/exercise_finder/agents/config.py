from exercise_finder.enums import AgentName, OpenAIModel, EventType
from exercise_finder.pydantic_models import ConversationEvent, UserMessageEvent, QuestionEvent

agent_name_to_model_mapping = {
    AgentName.GET_QUESTION_AGENT: OpenAIModel.GPT_5_MINI,
    AgentName.IMAGES_TO_QUESTION_AGENT: OpenAIModel.GPT_4O,
    AgentName.FORMAT_MULTIPART_QUESTION_AGENT: OpenAIModel.GPT_5_MINI,
}

# what agents receive what events as input
agent_name_to_event_mapping: dict[AgentName, list[type[ConversationEvent]]] = {
    AgentName.GET_QUESTION_AGENT: [UserMessageEvent, QuestionEvent],
    AgentName.IMAGES_TO_QUESTION_AGENT: [UserMessageEvent],
    AgentName.FORMAT_MULTIPART_QUESTION_AGENT: [UserMessageEvent],
}


# Event type ↔ model mappings used across persistence and adapters
event_type_to_model_mapping: dict[EventType, type[ConversationEvent]] = {
    EventType.USER_MESSAGE_EVENT: UserMessageEvent,
    EventType.QUESTION_EVENT: QuestionEvent,
}
