"""
Natural LLM Debate Simulator with Time-Based Free Participation
================================================================
This script simulates natural debates where agents can jump in freely based on
relevance and interest, rather than taking strict turns.
"""

import os
import time
from typing import List, Dict, Optional
from groq import Groq
from datetime import datetime, timedelta

topic_prompt = "You get a promotion that doubles your pay but triples your stress. Take the money or protect your sanity?"

class DebateAgent:
    """Represents a debate agent that can decide when to speak."""
    
    def __init__(self, name: str, client: Groq, model: str = "llama-3.3-70b-versatile"):
        self.name = name
        self.client = client
        self.model = model
        self.participation_count = 0
    
    def construct_system_prompt(self) -> str:
        """Creates system prompt that enforces ideal speech rules."""
        return f"""You are {self.name}, a participant in a natural, flowing debate following ideal speech rules:

IDEAL SPEECH RULES:
1. **Truthfulness**: Make only claims you believe to be true and can support with reasoning
2. **Sincerity**: Express your genuine understanding and beliefs
3. **Rationality**: Provide logical arguments and valid reasoning
4. **Comprehensibility**: Express ideas clearly and accessibly
5. **Respect**: Acknowledge others' arguments fairly before responding
6. **Good Faith**: Aim to reach mutual understanding, not just "win"
7. **No Fallacies**: Avoid ad hominem, strawman, and other logical fallacies
8. **Evidence-Based**: Support claims with reasoning or evidence when possible

This is a NATURAL debate; Try to have a substantive and lengthy debate. Make sure you equally contribute. Jump in with something:
- Substantive to add
- You disagree with a point
- You have a question for someone
- You can synthesize or clarify competing views
"""

    def should_participate(self, debate_topic: str, debate_history: List[Dict[str, str]]) -> tuple[bool, float]:
        """
        Decides if the agent should speak based on the current debate state.
        Returns (should_speak, confidence_score)
        """
        if not debate_history:
            # Everyone speaks in opening
            return True, 1.0
        
        # Don't speak if just spoke
        if debate_history and debate_history[-1]['speaker'] == self.name:
            return False, 0.0
        
        # if len(debate_history) <= 6:
        #    return True, 1.0
        
        # Build context
        recent_context = debate_history[-3:] if len(debate_history) >= 3 else debate_history
        context_text = "\n".join([f"{entry['speaker']}: {entry['statement']}" for entry in recent_context])
        
        decision_prompt = f"""Debate topic: {debate_topic}

Recent statements:
{context_text}

Question: Should you ({self.name}) speak now?

Respond with ONLY one of these options:
SPEAK - if you have a substantive point to make
PASS - if others should continue

Then on a new line, rate your confidence 0.0-1.0"""

        messages = [
            {"role": "system", "content": "You are deciding whether to participate in a debate turn."},
            {"role": "user", "content": decision_prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=50
            )
            
            decision_text = response.choices[0].message.content.strip()
            lines = decision_text.split('\n')
            
            should_speak = 'SPEAK' in lines[0].upper()
            
            # Extract confidence score
            confidence = 0.5
            for line in lines:
                try:
                    num = float(''.join(c for c in line if c.isdigit() or c == '.'))
                    if 0 <= num <= 1:
                        confidence = num
                        break
                except:
                    pass
            
            return should_speak, confidence
            
        except Exception as e:
            print(f"Error in participation decision: {e}")
            # Default: speak with low confidence if unsure
            return True, 0.3

    def generate_response(self, debate_topic: str, debate_history: List[Dict[str, str]]) -> str:
        """Generates a response following ideal speech constraints."""
        
        messages = [{"role": "system", "content": self.construct_system_prompt()}]
        
        # Build context
        if not debate_history:
            messages.append({
                "role": "user",
                "content": f"Opening statement on: '{debate_topic}'\n\nProvide your initial position (2-4 sentences)."
            })
        else:
            # Recent context only
            recent_statements = debate_history[-5:]
            context = f"Debate topic: {debate_topic}\n\nRecent discussion:\n"
            for entry in recent_statements:
                context += f"{entry['speaker']}: {entry['statement']}\n\n"
            
            context += "Your turn. Respond naturally and concisely (2-4 sentences)."
            messages.append({"role": "user", "content": context})
        
        # Get response
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=0.7,
            max_tokens=200
        )
        
        self.participation_count += 1
        return chat_completion.choices[0].message.content


class NaturalDebateSimulator:
    """Manages natural, free-flowing debates with time limits."""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.agents: List[DebateAgent] = []
        self.debate_history: List[Dict[str, str]] = []
    
    def add_agent(self, name: str):
        """Adds a debate agent to the simulation."""
        agent = DebateAgent(name, self.client, self.model)
        self.agents.append(agent)
    
    def run_timed_debate(self, topic: str, duration_minutes: int = 5, max_turns: int = 30):
        """
        Runs a natural debate with a time limit.
        Agents decide freely when to participate.
        """
        print("=" * 80)
        print(f"NATURAL DEBATE SIMULATION")
        print("=" * 80)
        print(f"\nTopic: {topic}")
        print(f"Participants: {', '.join([agent.name for agent in self.agents])}")
        print(f"Duration: {duration_minutes} minutes (max {max_turns} turns)")
        print(f"Format: Free participation - agents jump in when they have something to say")
        print("\n" + "=" * 80 + "\n")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        turn_count = 0
        
        # Phase 1: Opening statements (everyone speaks once)
        print("\n--- OPENING STATEMENTS ---\n")
        for agent in self.agents:
            print(f"[{agent.name}]:")
            try:
                response = agent.generate_response(topic, self.debate_history)
                print(f"{response}\n")
                
                self.debate_history.append({
                    "timestamp": datetime.now(),
                    "speaker": agent.name,
                    "statement": response,
                    "turn": turn_count
                })
                turn_count += 1
            except Exception as e:
                print(f"Error: {e}\n")
        
        # Phase 2: Natural discussion
        print("\n--- OPEN DISCUSSION ---\n")
        
        while datetime.now() < end_time and turn_count < max_turns:
            # Each agent decides if they want to speak
            candidates = []
            
            for agent in self.agents:
                try:
                    should_speak, confidence = agent.should_participate(topic, self.debate_history)
                    if should_speak:
                        candidates.append((agent, confidence))
                except Exception as e:
                    print(f"[Decision error for {agent.name}: {e}]")
            
            if not candidates:
                print("[No agent wishes to speak - debate naturally concluding]\n")
                break
            
            # Select agent with highest confidence
            candidates.sort(key=lambda x: x[1], reverse=True)
            selected_agent, confidence = candidates[0]
            
            # Generate response
            print(f"[{selected_agent.name}] (confidence: {confidence:.2f}):")
            try:
                response = selected_agent.generate_response(topic, self.debate_history)
                print(f"{response}\n")
                
                self.debate_history.append({
                    "timestamp": datetime.now(),
                    "speaker": selected_agent.name,
                    "statement": response,
                    "turn": turn_count,
                    "confidence": confidence
                })
                turn_count += 1
                
            except Exception as e:
                print(f"Error: {e}\n")
            
            # Brief pause to simulate natural conversation timing
            time.sleep(0.5)
        
        # End debate
        elapsed = (datetime.now() - start_time).total_seconds() / 60
        
        print("\n" + "=" * 80)
        print("DEBATE CONCLUDED")
        print("=" * 80)
        print(f"Duration: {elapsed:.1f} minutes")
        print(f"Total turns: {turn_count}")
        print(f"\nParticipation breakdown:")
        for agent in self.agents:
            percentage = (agent.participation_count / turn_count * 100) if turn_count > 0 else 0
            print(f"  {agent.name}: {agent.participation_count} turns ({percentage:.1f}%)")
        print()
    
    def generate_summary(self) -> str:
        """Generates a summary of the debate."""
        if not self.debate_history:
            return "No debate history to summarize."
        
        transcript = self._format_history()
        
        summary_prompt = f"""Analyze this natural debate and provide a summary:

Topic: [See transcript]

{transcript}

Provide a 2-3 paragraph summary covering:
1. Main positions and how they evolved
2. Key points of agreement and disagreement  
3. Quality of discourse and natural flow
4. Most compelling arguments made"""

        messages = [
            {"role": "system", "content": "You are an objective debate analyst."},
            {"role": "user", "content": summary_prompt}
        ]
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.5,
                max_tokens=500
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating summary: {e}"
    
    def _format_history(self) -> str:
        """Formats debate history as a readable transcript."""
        if not self.debate_history:
            return "No history available."
        
        transcript = ""
        for i, entry in enumerate(self.debate_history, 1):
            timestamp = entry['timestamp'].strftime("%H:%M:%S") if 'timestamp' in entry else ""
            confidence = f" [confidence: {entry['confidence']:.2f}]" if 'confidence' in entry else ""
            transcript += f"\n[{i}] {timestamp} - {entry['speaker']}{confidence}:\n{entry['statement']}\n"
        return transcript
    
    def save_transcript(self, filename: str = "natural_debate_transcript.txt"):
        """Saves the debate transcript to a file."""
        with open(filename, 'w') as f:
            f.write("NATURAL DEBATE TRANSCRIPT\n")
            f.write("=" * 80 + "\n\n")
            
            if self.debate_history:
                f.write(f"Topic: {self.debate_history[0] if self.debate_history else 'N/A'}\n\n")
            
            f.write(self._format_history())
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("ANALYSIS\n")
            f.write("=" * 80 + "\n\n")
            f.write(self.generate_summary())
        
        print(f"\nTranscript saved to: {filename}")


def main():
    """Main function to run the natural debate simulation."""
    
    # Get API key
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    # Initialize simulator
    simulator = NaturalDebateSimulator(api_key=api_key)
    
    # Add three agents
    simulator.add_agent("Alex")
    simulator.add_agent("Jordan")
    simulator.add_agent("Riley")
    
    # Define debate topic
    topic = topic_prompt
    
    # Run natural debate (5 minutes or 30 turns max)
    simulator.run_timed_debate(topic, duration_minutes=5, max_turns=30)
    
    # Generate and display summary
    # print("\n" + "=" * 80)
    # print("DEBATE ANALYSIS")
    # print("=" * 80 + "\n")
    # summary = simulator.generate_summary()
    # print(summary)
    
    # Save transcript
    simulator.save_transcript("debate_transcript_10.txt")


if __name__ == "__main__":
    main()