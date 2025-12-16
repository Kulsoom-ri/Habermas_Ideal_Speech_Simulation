"""
Simple Consensus Detection Script
"""

import re
from pathlib import Path
import sys


class SimpleConsensusDetector:
    """Detect consensus indicators in debate transcripts"""
    
    def __init__(self):
        # POSITIVE INDICATORS (suggest consensus/convergence)
        self.agreement_patterns = [
            r'\bI agree\b',
            r'\byou\'?re right\b',
            r'\bthat\'?s correct\b',
            r'\bexactly\b',
            r'\babsolutely\b',
            r'\bgood point\b',
            r'\bfair point\b',
            r'\bvalid point\b',
        ]
        
        self.building_patterns = [
            r'\bbuild on\b',
            r'\badd to\b',
            r'\bexpand on\b',
            r'\bbuilding on\b',
            r'\badding to\b',
        ]
        
        self.synthesis_patterns = [
            r'\bsynthesize\b',
            r'\bcombining\b',
            r'\bintegrat\w*\b',
            r'\bmerge\b',
            r'\bbring together\b',
            r'\bwe both\b',
            r'\bboth.*and\b',
        ]
        
        self.convergence_patterns = [
            r'\bwe can agree\b',
            r'\bwe agree\b',
            r'\bcommon ground\b',
            r'\bshared understanding\b',
            r'\breached consensus\b',
            r'\breached agreement\b',
        ]
        
        self.question_patterns = [
            r'\bcan you\b',
            r'\bcan we\b',
            r'\bcould you\b',
            r'\bwould you\b',
            r'\bI\'?d love to hear\b',
            r'\bwhat are your thoughts\b',
        ]
        
        # NEGATIVE INDICATORS (suggest disagreement/no consensus)
        self.disagreement_patterns = [
            r'\bI disagree\b',
            r'\bI don\'?t agree\b',
            r'\bthat\'?s wrong\b',
            r'\bthat\'?s incorrect\b',
            r'\bactually\b',
            r'\bin reality\b',
            r'\bthe truth is\b',
        ]
        
        self.opposition_patterns = [
            r'\bhowever\b',
            r'\bbut\b',
            r'\balthough\b',
            r'\bcontrary to\b',
            r'\bon the other hand\b',
        ]
    
    def parse_transcript(self, transcript: str) -> list:
        """Parse transcript into turns"""
        turns = []
        
        # Match format: [1] 07:05:57 - Alex:
        pattern = r'^\[\d+\]\s+[\d:]+\s+-\s+(.+?)(?:\s*\[confidence:\s*[\d.]+\])?\s*:\s*\n(.*?)(?=^\[\d+\]|\Z)'
        matches = re.findall(pattern, transcript, re.MULTILINE | re.DOTALL)
        
        for i, (speaker, content) in enumerate(matches, 1):
            turns.append({
                'turn': i,
                'speaker': speaker.strip(),
                'content': content.strip()
            })
        
        return turns
    
    def count_patterns(self, text: str, patterns: list) -> int:
        """Count pattern occurrences in text"""
        count = 0
        text_lower = text.lower()
        for pattern in patterns:
            count += len(re.findall(pattern, text_lower))
        return count
    
    def analyze_consensus(self, transcript: str) -> dict:
        """Analyze transcript for consensus indicators"""
        
        turns = self.parse_transcript(transcript)
        
        if len(turns) < 2:
            return {
                'consensus_type': 'insufficient_data',
                'consensus_score': 0.0,
                'total_turns': len(turns),
                'details': 'Need at least 2 turns to detect consensus'
            }
        
        # Combine all text
        all_text = ' '.join(t['content'] for t in turns)
        
        # Count positive indicators
        agreements = self.count_patterns(all_text, self.agreement_patterns)
        building = self.count_patterns(all_text, self.building_patterns)
        synthesis = self.count_patterns(all_text, self.synthesis_patterns)
        convergence = self.count_patterns(all_text, self.convergence_patterns)
        questions = self.count_patterns(all_text, self.question_patterns)
        
        # Count negative indicators
        disagreements = self.count_patterns(all_text, self.disagreement_patterns)
        oppositions = self.count_patterns(all_text, self.opposition_patterns)
        
        # Calculate scores
        positive_score = (
            agreements * 3 +
            building * 2 +
            synthesis * 3 +
            convergence * 4 +
            questions * 0.5
        )
        
        negative_score = (
            disagreements * 3 +
            oppositions * 0.3
        )
        
        # Normalize to 0-1 scale
        max_positive = 50
        consensus_score = positive_score / max_positive
        consensus_score -= negative_score / 20
        consensus_score = max(0, min(1, consensus_score))
        
        # Classify consensus type
        if consensus_score >= 0.7:
            consensus_type = 'STRONG_CONSENSUS'
        elif consensus_score >= 0.5:
            consensus_type = 'MODERATE_CONSENSUS'
        elif consensus_score >= 0.3:
            consensus_type = 'PARTIAL_CONSENSUS'
        elif disagreements > 3:
            consensus_type = 'EXPLICIT_DISAGREEMENT'
        else:
            consensus_type = 'NO_CONSENSUS'
        
        return {
            'consensus_type': consensus_type,
            'consensus_score': consensus_score,
            'total_turns': len(turns),
            'positive_indicators': {
                'agreements': agreements,
                'building_on_points': building,
                'synthesis_attempts': synthesis,
                'convergence_statements': convergence,
                'questions_asked': questions,
            },
            'negative_indicators': {
                'disagreements': disagreements,
                'opposition_phrases': oppositions,
            },
            'speakers': list(set(t['speaker'] for t in turns))
        }
    
    def print_report(self, results: dict):
        """Print consensus analysis report"""
        
        print("\n" + "="*80)
        print("CONSENSUS ANALYSIS")
        print("="*80)
        
        print(f"\nConsensus Type: {results['consensus_type'].replace('_', ' ')}")
        print(f"Consensus Score: {results['consensus_score']:.2f}/1.0")
        print(f"Total Turns: {results['total_turns']}")
        print(f"Speakers: {', '.join(results['speakers'])}")
        
        if results['consensus_type'] == 'insufficient_data':
            print(f"\nDetails: {results['details']}")
            return
        
        print("\nPositive Indicators:")
        pos = results['positive_indicators']
        print(f"  Agreement phrases: {pos['agreements']}")
        print(f"  Building on points: {pos['building_on_points']}")
        print(f"  Synthesis attempts: {pos['synthesis_attempts']}")
        print(f"  Convergence statements: {pos['convergence_statements']}")
        print(f"  Questions asked: {pos['questions_asked']}")
        
        print("\nNegative Indicators:")
        neg = results['negative_indicators']
        print(f"  Disagreement phrases: {neg['disagreements']}")
        print(f"  Opposition phrases: {neg['opposition_phrases']}")
        
        print("\nInterpretation:")
        if results['consensus_type'] == 'STRONG_CONSENSUS':
            print("  ✅ Strong evidence of consensus")
        elif results['consensus_type'] == 'MODERATE_CONSENSUS':
            print("  ✅ Moderate consensus")
        elif results['consensus_type'] == 'PARTIAL_CONSENSUS':
            print("  ⚠️  Partial consensus")
        elif results['consensus_type'] == 'EXPLICIT_DISAGREEMENT':
            print("  ❌ No consensus - explicit disagreement")
        else:
            print("  ❌ No consensus")
        
        print("\n" + "="*80)


def main():
    """Process transcripts"""
    
    # CONFIGURE PATHS HERE
    # Option 1: Specify transcript directory
    transcript_dir = "debatewithoutconstraints_transcripts"  # Change this to folder name
    
    # Option 2: Or pass as command line argument
    if len(sys.argv) > 1:
        transcript_dir = sys.argv[1]
    
    path = Path(transcript_dir)
    
    if not path.exists():
        print(f"Error: Directory not found: {path}")
        print(f"Current directory: {Path.cwd()}")
        print(f"\nPlease update the 'transcript_dir' variable in the script")
        print(f"or run: python consensus_detection.py <your_transcript_folder>")
        sys.exit(1)
    
    detector = SimpleConsensusDetector()
    
    # Handle single file
    if path.is_file():
        print(f"Analyzing: {path.name}")
        
        with open(path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        results = detector.analyze_consensus(transcript)
        detector.print_report(results)
        return
    
    # Handle directory
    if path.is_dir():
        files = sorted(path.glob("*.txt"))
        
        if not files:
            print(f"No .txt files found in {path}")
            return
        
        print(f"Found {len(files)} transcript files in {path}")
        print("="*80 + "\n")
        
        all_results = []
        
        for filepath in files:
            print(f"\nAnalyzing: {filepath.name}")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    transcript = f.read()
                
                results = detector.analyze_consensus(transcript)
                results['filename'] = filepath.name
                all_results.append(results)
                
                # Print brief summary
                print(f"  Type: {results['consensus_type'].replace('_', ' ')}")
                print(f"  Score: {results['consensus_score']:.2f}")
                
            except Exception as e:
                print(f"  ERROR: {e}")
        
        # Full reports
        print("\n" + "="*80)
        print("DETAILED REPORTS")
        print("="*80)
        
        for result in all_results:
            print(f"\n{'='*80}")
            print(f"FILE: {result['filename']}")
            detector.print_report(result)
        
        # Summary
        if all_results:
            print("\n" + "="*80)
            print("SUMMARY ACROSS ALL TRANSCRIPTS")
            print("="*80 + "\n")
            
            consensus_types = {}
            for r in all_results:
                ctype = r['consensus_type']
                consensus_types[ctype] = consensus_types.get(ctype, 0) + 1
            
            print("Consensus Distribution:")
            for ctype, count in sorted(consensus_types.items()):
                print(f"  {ctype.replace('_', ' ')}: {count}")
            
            avg_score = sum(r['consensus_score'] for r in all_results) / len(all_results)
            print(f"\nAverage Consensus Score: {avg_score:.2f}/1.0")
            
            # Export to CSV
            import csv
            csv_path = path / "consensus_analysis.csv"
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'filename',
                    'consensus_type',
                    'consensus_score',
                    'agreements',
                    'building',
                    'synthesis',
                    'convergence',
                    'questions',
                    'disagreements'
                ])
                
                for r in all_results:
                    pos = r['positive_indicators']
                    neg = r['negative_indicators']
                    writer.writerow([
                        r['filename'],
                        r['consensus_type'],
                        f"{r['consensus_score']:.2f}",
                        pos['agreements'],
                        pos['building_on_points'],
                        pos['synthesis_attempts'],
                        pos['convergence_statements'],
                        pos['questions_asked'],
                        neg['disagreements']
                    ])
            
            print(f"\n✓ Exported to: {csv_path}")
            print("="*80)


if __name__ == "__main__":
    main()