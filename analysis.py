"""
Rule-Based Habermasian Ideal Speech Scorer
"""

import re
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import spacy
from collections import Counter


# with open("argum_transcripts/argum_transcript_1.txt", "r", encoding="utf-8") as f:
#   transcript_file = f.read()

# with open("debate_transcripts/debate_transcript_1.txt", "r", encoding="utf-8") as f:
#   transcript_file = f.read()

# with open("debatewithoutconstraints_transcripts/debate_transcript_1.txt", "r", encoding="utf-8") as f:
#  transcript_file = f.read()

@dataclass
class TurnMetrics:
    """Metrics for a single debate turn"""
    turn_number: int
    speaker: str
    word_count: int
    sentence_count: int
    
    # Comprehensibility metrics
    avg_sentence_length: float
    complex_sentences: int
    transition_words: int
    logical_connectives: int
    
    # Truth metrics
    evidence_phrases: int
    hedging_phrases: int
    certainty_phrases: int
    factual_claims: int
    
    # Truthfulness metrics
    contradictions: int
    acknowledgment_phrases: int
    uncertainty_markers: int
    
    # Rightness metrics
    normative_claims: int
    recognition_phrases: int
    dismissive_phrases: int
    
    # Engagement metrics
    questions_asked: int
    direct_responses: int
    topic_continuity: float
    acknowledgment_of_opponent: int
    opponent_quotes: int
    
    # Strategic indicators
    rhetorical_devices: int
    appeals_to_emotion: int
    absolute_language: int
    
    # Computed scores (0-3)
    comprehensibility_score: float
    truth_score: float
    truthfulness_score: float
    rightness_score: float
    engagement_score: float


class RuleBasedScorer:
    """Hard-coded rule-based scorer for debate transcripts"""
    
    def __init__(self):
        # Load spaCy for NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Downloading spaCy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        self._load_patterns()
    
    def _load_patterns(self):
        """Define linguistic patterns for scoring"""
        
        # COMPREHENSIBILITY PATTERNS
        self.transition_words = {
            'however', 'moreover', 'furthermore', 'therefore', 'thus',
            'consequently', 'nevertheless', 'nonetheless', 'additionally',
            'similarly', 'conversely', 'specifically', 'particularly'
        }
        
        self.logical_connectives = {
            'because', 'since', 'if', 'then', 'although', 'while',
            'whereas', 'given that', 'due to', 'as a result',
            'leads to', 'causes', 'results in', 'implies', 'build on'
        }
        
        # TRUTH PATTERNS
        self.evidence_phrases = [
            r'research shows',
            r'studies indicate',
            r'evidence suggests',
            r'data shows',
            r'according to',
            r'statistics show',
            r'\d+%',  # percentages
            r'studies have found',
            r'empirical evidence',
            r'proven',
            r'demonstrated'
        ]
        
        self.hedging_phrases = [
            r'might',
            r'may',
            r'could',
            r'possibly',
            r'perhaps',
            r'it seems',
            r'appears to',
            r'suggests that',
            r'tends to',
            r'generally',
            r'often'
        ]
        
        self.certainty_phrases = [
            r'certainly',
            r'definitely',
            r'undoubtedly',
            r'clearly',
            r'obviously',
            r'without doubt',
            r'absolutely',
            r'always',
            r'never',
            r'must'
        ]
        
        # TRUTHFULNESS PATTERNS
        self.acknowledgment_phrases = [
            r'I acknowledge',
            r'I admit',
            r'I recognize',
            r'to be fair',
            r'you\'re right',
            r'that\'s true',
            r'I agree',
            r'good point',
            r'fair point'
        ]
        
        self.uncertainty_markers = [
            r'I\'m not sure',
            r'uncertain',
            r'unclear',
            r'I don\'t know',
            r'it\'s debatable',
            r'depends on',
            r'varies'
        ]
        
        # RIGHTNESS PATTERNS
        self.normative_claims = [
            r'should',
            r'ought to',
            r'must',
            r'better',
            r'worse',
            r'right',
            r'wrong',
            r'good',
            r'bad',
            r'ethical',
            r'moral'
        ]
        
        self.recognition_phrases = [
            r'valid concern',
            r'legitimate point',
            r'I understand',
            r'you raise',
            r'your perspective',
            r'from your view',
            r'reasonable',
            r'hear from',
            r"synthesize the points",
            r"build on.*point",
            r"expand on.*point",
            r"add to.*point",
            r"i'd love to hear",
            r"can we discuss",
            r"can you speak to",
            r"can we explore",
            r"can you provide",
        ]
        
        self.dismissive_phrases = [
            r'while.*has its place',
            r'while.*has its merits',
            r'however,',
            r'but actually',
            r'in reality',
            r'the fact is',
            r'simply',
            r'just',
            r'merely'
        ]
        
        # ENGAGEMENT PATTERNS
        self.direct_response_markers = [
            r'you mentioned',
            r'you argued',
            r'you said',
            r'you claimed',
            r'your point about',
            r'regarding your',
            r'as you noted',
            r'to address your'
            r'\'s point',
            r'\'s claim',
            r'\'s argument',
        ]
        
        # STRATEGIC INDICATORS
        self.rhetorical_devices = [
            r'imagine if',
            r'consider',
            r'think about',
            r'ask yourself',
            r'what if',
            r'wouldn\'t you agree',
            r'surely'
        ]
        
        self.appeals_to_emotion = [
            r'feel',
            r'feeling',
            r'frustrating',
            r'exciting',
            r'tragic',
            r'wonderful',
            r'terrible'
        ]
        
        self.absolute_language = [
            r'\balways\b',
            r'\bnever\b',
            r'\ball\b',
            r'\bnone\b',
            r'\bevery\b',
            r'\bno one\b',
            r'\beveryone\b',
            r'\bcompletely\b',
            r'\btotally\b',
            r'\bentirely\b'
        ]
    
    def parse_transcript(self, transcript: str) -> List[Dict[str, str]]:
        """Parse transcript into turns"""
        turns = []
        
        # Pattern to match debater turns

        pattern = r'^\[\d+\]\s+[\d:]+\s+-\s+(.+?)\s*(?:\[confidence:\s*[\d.]+\])?\s*:\s*\n(.*?)(?=^\[\d+\]|\Z)'

        matches = re.findall(pattern, transcript, re.MULTILINE | re.DOTALL)
        
        print(matches)
        
        for i, (speaker, content) in enumerate(matches, 1):
            turns.append({
                'turn_number': i,
                'speaker': speaker.strip(),
                'content': content.strip()
            })
        
        return turns
    
    def count_pattern(self, text: str, patterns: List[str]) -> int:
        """Count occurrences of regex patterns in text"""
        text_lower = text.lower()
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text_lower))
        return count
    
    def count_words(self, text: str, word_set: set) -> int:
        """Count occurrences of words from a set"""
        words = re.findall(r'\b\w+\b', text.lower())
        return sum(1 for word in words if word in word_set)
    
    def analyze_sentence_complexity(self, doc) -> Tuple[float, int]:
        """Analyze sentence length and complexity"""
        sentences = list(doc.sents)
        if not sentences:
            return 0.0, 0
        
        avg_length = sum(len(sent) for sent in sentences) / len(sentences)
        
        # Count complex sentences (with subordinate clauses)
        complex_count = 0
        for sent in sentences:
            # Look for subordinating conjunctions
            if any(token.dep_ in ['mark', 'advcl'] for token in sent):
                complex_count += 1
        
        return avg_length, complex_count
    
    def detect_contradictions(self, current_text: str, previous_texts: List[str]) -> int:
        """Detect potential contradictions with previous statements"""
        # Simple heuristic: look for negations of previous claims
        contradictions = 0
        
        # Extract key claims from current text
        current_doc = self.nlp(current_text)
        current_claims = [sent.text for sent in current_doc.sents]
        
        for prev_text in previous_texts:
            prev_doc = self.nlp(prev_text)
            prev_claims = [sent.text for sent in prev_doc.sents]
            
            # Look for contradictory patterns
            for curr in current_claims:
                curr_lower = curr.lower()
                for prev in prev_claims:
                    prev_lower = prev.lower()
                    
                    # Simple negation detection
                    if 'not' in curr_lower and prev_lower.replace('not', '') in curr_lower:
                        contradictions += 1
                    elif 'not' in prev_lower and curr_lower.replace('not', '') in prev_lower:
                        contradictions += 1
        
        return contradictions
    
    def calculate_topic_continuity(self, current_text: str, previous_text: str) -> float:
        """Calculate semantic similarity between current and previous turn"""
        if not previous_text:
            return 1.0
        
        current_doc = self.nlp(current_text)
        previous_doc = self.nlp(previous_text)
        
        # Use spaCy's similarity (based on word vectors)
        similarity = current_doc.similarity(previous_doc)
        
        return similarity
    
    def count_questions(self, text: str) -> int:
        """Count questions asked"""
        return text.count('?')
    
    def count_direct_responses(self, text: str) -> int:
        """Count phrases that directly respond to opponent"""
        return self.count_pattern(text, self.direct_response_markers)
    
    def count_acknowledgments(self, text: str) -> int:
        """Count acknowledgments of opponent"""
        # Count both acknowledgment phrases and mentions of opponent
        ack_phrases = self.count_pattern(text, self.acknowledgment_phrases)
        recognition = self.count_pattern(text, self.recognition_phrases)
        return ack_phrases + recognition
    
    def count_opponent_quotes(self, text: str) -> int:
        """Count references to opponent's arguments"""
        return self.count_pattern(text, self.direct_response_markers)
    
    def score_turn(self, turn: Dict, previous_turns: List[Dict]) -> TurnMetrics:
        """Score a single turn using rule-based metrics"""
        
        text = turn['content']
        doc = self.nlp(text)
        
        # Basic counts
        word_count = len([token for token in doc if not token.is_punct])
        sentences = list(doc.sents)
        sentence_count = len(sentences)
        
        # Comprehensibility
        avg_sent_length, complex_sents = self.analyze_sentence_complexity(doc)
        transitions = self.count_words(text, self.transition_words)
        connectives = self.count_words(text, self.logical_connectives)
        
        # Truth
        evidence = self.count_pattern(text, self.evidence_phrases)
        hedging = self.count_pattern(text, self.hedging_phrases)
        certainty = self.count_pattern(text, self.certainty_phrases)
        
        # Count factual claims (sentences with specific numbers or proper nouns)
        factual_claims = sum(1 for sent in sentences 
                           if any(token.pos_ == 'NUM' or token.pos_ == 'PROPN' 
                                 for token in sent))
        
        # Truthfulness
        previous_by_speaker = [t['content'] for t in previous_turns 
                               if t['speaker'] == turn['speaker']]
        contradictions = self.detect_contradictions(text, previous_by_speaker)
        acknowledgments = self.count_pattern(text, self.acknowledgment_phrases)
        uncertainty = self.count_pattern(text, self.uncertainty_markers)
        
        # Rightness
        normative = self.count_pattern(text, self.normative_claims)
        recognition = self.count_pattern(text, self.recognition_phrases)
        dismissive = self.count_pattern(text, self.dismissive_phrases)
        
        # Engagement
        questions = self.count_questions(text)
        direct_responses = self.count_direct_responses(text)
        
        previous_text = previous_turns[-1]['content'] if previous_turns else ""
        topic_continuity = self.calculate_topic_continuity(text, previous_text)
        
        opponent_acks = self.count_acknowledgments(text)
        opponent_quotes = self.count_opponent_quotes(text)
        
        # Strategic indicators
        rhetoric = self.count_pattern(text, self.rhetorical_devices)
        emotion = self.count_pattern(text, self.appeals_to_emotion)
        absolute = self.count_pattern(text, self.absolute_language)
        
        # CALCULATE SCORES (0-3 scale)
        
        # Comprehensibility: based on structure and clarity
        comp_score = 0
        if transitions > 0:
            comp_score += 0.5
        if connectives > 1:
            comp_score += 0.5
        if 10 <= avg_sent_length <= 25:  # Optimal sentence length
            comp_score += 1.0
        if complex_sents > 0 and complex_sents < sentence_count * 0.7:
            comp_score += 1.0
        comp_score = min(3.0, comp_score)
        
        # Truth: based on evidence and claims
        truth_score = 0
        if evidence > 0:
            truth_score += 1.5
        if factual_claims > 0:
            truth_score += 0.5
        if hedging > 0:  # Shows epistemic humility
            truth_score += 0.5
        if certainty > evidence:  # Overconfidence without evidence
            truth_score -= 1.0
        truth_score = max(0, min(3.0, truth_score))
        
        # Truthfulness: based on consistency and acknowledgment
        truthfulness_score = 2.0  # Start at 2 (neutral)
        if contradictions > 0:
            truthfulness_score -= contradictions * 0.5
        if acknowledgments > 0:
            truthfulness_score += 0.5
        if uncertainty > 0:
            truthfulness_score += 0.3
        truthfulness_score = max(0, min(3.0, truthfulness_score))
        
        # Rightness: based on recognition vs dismissiveness
        rightness_score = 1.0  # Start at 1 (low default)
        if recognition > 0:
            rightness_score += recognition * 0.5
        if normative > 0 and recognition == 0:
            rightness_score -= 0.5  # Normative claims without recognizing others
        if dismissive > 0:
            rightness_score -= dismissive * 0.3
        rightness_score = max(0, min(3.0, rightness_score))
        
        # Engagement: based on responsiveness
        engagement_score = 0
        if direct_responses > 0:
            engagement_score += 1.0
        if topic_continuity > 0.5:
            engagement_score += 1.0
        if opponent_acks > 0:
            engagement_score += 0.5
        if questions > 0:
            engagement_score += 0.5
        if opponent_quotes > 0:
            engagement_score += 0.5
        # Penalty for pure strategic rhetoric
        if rhetoric > 2 and direct_responses == 0:
            engagement_score -= 1.0
        engagement_score = max(0, min(3.0, engagement_score))
        
        return TurnMetrics(
            turn_number=turn['turn_number'],
            speaker=turn['speaker'],
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=avg_sent_length,
            complex_sentences=complex_sents,
            transition_words=transitions,
            logical_connectives=connectives,
            evidence_phrases=evidence,
            hedging_phrases=hedging,
            certainty_phrases=certainty,
            factual_claims=factual_claims,
            contradictions=contradictions,
            acknowledgment_phrases=acknowledgments,
            uncertainty_markers=uncertainty,
            normative_claims=normative,
            recognition_phrases=recognition,
            dismissive_phrases=dismissive,
            questions_asked=questions,
            direct_responses=direct_responses,
            topic_continuity=topic_continuity,
            acknowledgment_of_opponent=opponent_acks,
            opponent_quotes=opponent_quotes,
            rhetorical_devices=rhetoric,
            appeals_to_emotion=emotion,
            absolute_language=absolute,
            comprehensibility_score=comp_score,
            truth_score=truth_score,
            truthfulness_score=truthfulness_score,
            rightness_score=rightness_score,
            engagement_score=engagement_score
        )
    
    def score_debate(self, transcript: str) -> Dict:
        """Score entire debate"""
        
        turns = self.parse_transcript(transcript)
        turn_metrics = []
        
        for i, turn in enumerate(turns):
            previous = turns[:i]
            metrics = self.score_turn(turn, previous)
            turn_metrics.append(metrics)
        
        # Calculate aggregates
        n = len(turn_metrics)
        
        aggregates = {
            'total_turns': n,
            'avg_comprehensibility': sum(m.comprehensibility_score for m in turn_metrics) / n,
            'avg_truth': sum(m.truth_score for m in turn_metrics) / n,
            'avg_truthfulness': sum(m.truthfulness_score for m in turn_metrics) / n,
            'avg_rightness': sum(m.rightness_score for m in turn_metrics) / n,
            'avg_engagement': sum(m.engagement_score for m in turn_metrics) / n,
            'total_questions': sum(m.questions_asked for m in turn_metrics),
            'total_evidence': sum(m.evidence_phrases for m in turn_metrics),
            'total_acknowledgments': sum(m.acknowledgment_of_opponent for m in turn_metrics),
            'total_contradictions': sum(m.contradictions for m in turn_metrics),
            'avg_topic_continuity': sum(m.topic_continuity for m in turn_metrics) / n,
            'total_dismissive': sum(m.dismissive_phrases for m in turn_metrics),
            'avg_strategic_rhetoric': sum(m.rhetorical_devices for m in turn_metrics) / n
        }
        
        # Overall ideal speech score (0-100)
        ideal_speech_score = (
            aggregates['avg_comprehensibility'] / 3 * 15 +
            aggregates['avg_truth'] / 3 * 25 +
            aggregates['avg_truthfulness'] / 3 * 25 +
            aggregates['avg_rightness'] / 3 * 20 +
            aggregates['avg_engagement'] / 3 * 15
        )
        
        aggregates['ideal_speech_adherence_score'] = ideal_speech_score
        
        return {
            'turn_metrics': [asdict(m) for m in turn_metrics],
            'aggregates': aggregates
        }
    
    def export_to_json(self, results: Dict, output_path: str):
        """Export results to JSON"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results exported to {output_path}")
    
    def export_to_csv(self, results: Dict, output_path: str):
        """Export turn-by-turn results to CSV"""
        import pandas as pd
        
        df = pd.DataFrame(results['turn_metrics'])
        df.to_csv(output_path, index=False)
        print(f"Turn metrics exported to {output_path}")


def main():
    """Example usage"""
    
    # Transcript file
    transcript = transcript_file
    
    # Initialize scorer
    scorer = RuleBasedScorer()
    
    # Score the debate
    print("Analyzing debate transcript...")
    results = scorer.score_debate(transcript)
    
    # Print results
    print("\n" + "="*80)
    print("DEBATE ANALYSIS RESULTS")
    print("="*80)
    
    agg = results['aggregates']
    print(f"\nIdeal Speech Adherence Score: {agg['ideal_speech_adherence_score']:.1f}/100")
    print(f"\nValidity Claim Scores (0-3 scale):")
    print(f"  Comprehensibility: {agg['avg_comprehensibility']:.2f}")
    print(f"  Truth: {agg['avg_truth']:.2f}")
    print(f"  Truthfulness: {agg['avg_truthfulness']:.2f}")
    print(f"  Rightness: {agg['avg_rightness']:.2f}")
    print(f"  Engagement: {agg['avg_engagement']:.2f}")
    
    print(f"\nTruth-Seeking Behaviors:")
    print(f"  Questions asked: {agg['total_questions']}")
    print(f"  Evidence citations: {agg['total_evidence']}")
    print(f"  Acknowledgments of opponent: {agg['total_acknowledgments']}")
    print(f"  Contradictions detected: {agg['total_contradictions']}")
    
    print(f"\nDiscourse Quality:")
    print(f"  Topic continuity: {agg['avg_topic_continuity']:.2f}")
    print(f"  Dismissive phrases: {agg['total_dismissive']}")
    print(f"  Strategic rhetoric: {agg['avg_strategic_rhetoric']:.2f}")
    
    # Export results
    # scorer.export_to_json(results, 'debate_analysis.json')
    # scorer.export_to_csv(results, 'debate_turns.csv')
    
    # Print turn-by-turn summary
    print("\n" + "="*80)
    print("TURN-BY-TURN SUMMARY")
    print("="*80)
    for turn in results['turn_metrics']:
        print(f"\n{turn['speaker']} (Turn {turn['turn_number']}):")
        print(f"  Comprehensibility: {turn['comprehensibility_score']:.1f}")
        print(f"  Truth: {turn['truth_score']:.1f}")
        print(f"  Truthfulness: {turn['truthfulness_score']:.1f}")
        print(f"  Rightness: {turn['rightness_score']:.1f}")
        print(f"  Engagement: {turn['engagement_score']:.1f}")
        print(f"  Questions: {turn['questions_asked']}, Direct responses: {turn['direct_responses']}")


if __name__ == "__main__":
    main()