from watson_developer_cloud import ConversationV1
import json

class ConversationAPI:
    def __init__(self,
                 workspace_id):
        self.workspace_id = workspace_id
        self.conversation =  ConversationV1(
            username='351251b5-22a9-4f30-9d04-884aff0aae4a',
            password='zwgLdqOlcfYi',
            version='2016-09-20'
        )

        # user id to watson context
        self.context_map = dict()

    def lookup(self,user_id):
        if user_id not in self.context_map:
            self.context_map[user_id] = {}
        return self.context_map[user_id]
    # Send message to watson conversation agent
    def message(self,
                user_id,
                message):
        response = self.conversation.message(
            workspace_id=self.workspace_id,
            message_input={'text': message},
            context=self.lookup(user_id)
        )
        self.context_map[user_id] = response['context']

        print json.dumps(response)
        return ''.join(response['output']['text'])



    
if __name__ == '__main__':
    workspace_id = '85ba0890-6fa8-4ca7-87af-b1b92cb6d10f'
    watson = ConversationAPI(workspace_id)
    print watson.message(1, "is the seas welcome day mandatory?")
    print watson.message(1, "When we hear about the UAH application?")    

        
