import watson
import nlp
from response_builder import ResponseBuilder

class Engine:
    def __init__(self,
                 training_data_path,
                 intent_confidence_thresh = .25):
        self.response_builder = ResponseBuilder(training_data_path)
        self.intent_thresh = intent_confidence_thresh
        self.conversation_context = {}
        self.watson = watson.ConversationAPI(watson.graduate_affairs_2_config())

    def initialize_context(self, conv_id):
        if conv_id not in self.conversation_context:
            v = {'entities':set(), 'intent':None, 'response':None}
            self.conversation_context[conv_id] = v

    def clear_context(self, conv_id):
        self.conversation_context.pop(conv_id, None)
            

    def extract_entities(self, conv_id, response):
        entities = [x['entity'] for x in response['entities']]
        self.conversation_context[conv_id]['entities'].update(entities)

    
    def extract_intent(self, conv_id, response):
        intents = [x['intent'] for x in response['intents'] if x['confidence'] > self.intent_thresh]
        if len(intents) > 0:
            self.conversation_context[conv_id]['intent'] = intents[0]

    def preprocess_token(self, token):
        token = nlp.strip_nonalpha_numeric(token)
        # TODO Add autocorrect. Word might be mispelled..Integrate in nlp component not here.
        return token

        
    def preprocess_sentence(self, sentence):
        tokens = nlp.tokenize_text(sentence)
        ret = ""
        for token in tokens:
            ret += self.preprocess_token(token) + " "
        return ret.strip()
            
        
        
    def process_message(self, conv_id, message):
        
        self.initialize_context(conv_id)
        sentences = nlp.get_sentences(message)
        for sentence in sentences:
            clean_sentence = self.preprocess_sentence(sentence)
            watson_response = self.watson.json_response(conv_id, clean_sentence)
            self.extract_entities(conv_id, watson_response)
            if nlp.sentence_is_question(sentence):
                self.extract_intent(conv_id,watson_response)
                context = self.conversation_context[conv_id]
                intent = context['intent']
                entities = list(context['entities'])
                self.conversation_context[conv_id]['response'] = \
                                                                 self.response_builder.get_best_response(intent, entities)
                return self.conversation_context[conv_id]
            
        return self.conversation_context[conv_id]
                
            
            
def read_tsv(fname):
    import csv
    l = []
    with open(fname, 'r') as f:
        tsv = csv.reader(f, delimiter='\t')
        for line in tsv:
            l.append(line)
    return l

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('traintsv')
    args = parser.parse_args()
    data = read_tsv(args.traintsv)

    # initialize engine
    engine = Engine(args.traintsv)
    
    for i, line in enumerate(data):
        query = line[0]
        print "Query: ", query
        print engine.process_message(i, query)
        
    
  
if __name__ == "__main__":
    main()
