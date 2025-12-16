"""
Batch Analyzer for RuleBasedScorer
Processes all transcripts in a directory and calculates average scores
"""

from pathlib import Path
import sys

# Import your scorer
from analysis import RuleBasedScorer


def batch_analyze(transcript_directory: str):
    """
    Analyze all transcripts in a directory and report averages
    """
    
    scorer = RuleBasedScorer()
    transcript_dir = Path(transcript_directory)
    
    # Find all transcript files
    transcript_files = sorted(transcript_dir.glob("*.txt"))
    
    if not transcript_files:
        print(f"No .txt files found in {transcript_directory}")
        return
    
    print(f"Found {len(transcript_files)} transcript files")
    print("="*80)
    print("Processing transcripts...")
    print("="*80 + "\n")
    
    # Store all results
    all_results = []
    failed_files = []
    
    # Process each file
    for i, filepath in enumerate(transcript_files, 1):
        print(f"[{i}/{len(transcript_files)}] {filepath.name}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                transcript = f.read()
            
            result = scorer.score_debate(transcript)
            result['filename'] = filepath.name
            all_results.append(result)
            
            # Print quick summary
            score = result['aggregates']['ideal_speech_adherence_score']
            print(f"  ✓ Score: {score:.1f}/100\n")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            failed_files.append(filepath.name)
    
    if not all_results:
        print("\n❌ No successful analyses!")
        return
    
    print("="*80)
    print(f"✓ Successfully analyzed {len(all_results)}/{len(transcript_files)} debates")
    if failed_files:
        print(f"✗ Failed: {', '.join(failed_files)}")
    print("="*80 + "\n")
    
    # Print individual results
    print("="*80)
    print("INDIVIDUAL DEBATE SCORES")
    print("="*80 + "\n")
    
    for result in all_results:
        agg = result['aggregates']
        print(f"{result['filename']}")
        print(f"  Ideal Speech Score: {agg['ideal_speech_adherence_score']:.1f}/100")
        print(f"  Comprehensibility: {agg['avg_comprehensibility']:.2f} | "
              f"Truth: {agg['avg_truth']:.2f} | "
              f"Truthfulness: {agg['avg_truthfulness']:.2f} | "
              f"Rightness: {agg['avg_rightness']:.2f} | "
              f"Engagement: {agg['avg_engagement']:.2f}")
        print(f"  Questions: {agg['total_questions']} | "
              f"Evidence: {agg['total_evidence']} | "
              f"Acknowledgments: {agg['total_acknowledgments']} | "
              f"Dismissive: {agg['total_dismissive']}")
        print()
    
    # Calculate averages
    n = len(all_results)
    
    avg_ideal_speech = sum(r['aggregates']['ideal_speech_adherence_score'] for r in all_results) / n
    avg_comprehensibility = sum(r['aggregates']['avg_comprehensibility'] for r in all_results) / n
    avg_truth = sum(r['aggregates']['avg_truth'] for r in all_results) / n
    avg_truthfulness = sum(r['aggregates']['avg_truthfulness'] for r in all_results) / n
    avg_rightness = sum(r['aggregates']['avg_rightness'] for r in all_results) / n
    avg_engagement = sum(r['aggregates']['avg_engagement'] for r in all_results) / n
    
    total_questions = sum(r['aggregates']['total_questions'] for r in all_results)
    total_evidence = sum(r['aggregates']['total_evidence'] for r in all_results)
    total_acknowledgments = sum(r['aggregates']['total_acknowledgments'] for r in all_results)
    total_contradictions = sum(r['aggregates']['total_contradictions'] for r in all_results)
    total_dismissive = sum(r['aggregates']['total_dismissive'] for r in all_results)
    
    avg_topic_continuity = sum(r['aggregates']['avg_topic_continuity'] for r in all_results) / n
    avg_strategic_rhetoric = sum(r['aggregates']['avg_strategic_rhetoric'] for r in all_results) / n
    
    # Print averages in the exact format requested
    print("="*80)
    print("AVERAGE ACROSS ALL DEBATES")
    print("="*80)
    print(f"\nIdeal Speech Adherence Score: {avg_ideal_speech:.1f}/100")
    
    print(f"\nValidity Claim Scores (0-3 scale):")
    print(f"  Comprehensibility: {avg_comprehensibility:.2f}")
    print(f"  Truth: {avg_truth:.2f}")
    print(f"  Truthfulness: {avg_truthfulness:.2f}")
    print(f"  Rightness: {avg_rightness:.2f}")
    print(f"  Engagement: {avg_engagement:.2f}")
    
    print(f"\nTruth-Seeking Behaviors:")
    print(f"  Questions asked: {total_questions // n} (avg per debate: {total_questions/n:.1f})")
    print(f"  Evidence citations: {total_evidence // n} (avg per debate: {total_evidence/n:.1f})")
    print(f"  Acknowledgments of opponent: {total_acknowledgments // n} (avg per debate: {total_acknowledgments/n:.1f})")
    print(f"  Contradictions detected: {total_contradictions // n} (avg per debate: {total_contradictions/n:.1f})")
    
    print(f"\nDiscourse Quality:")
    print(f"  Topic continuity: {avg_topic_continuity:.2f}")
    print(f"  Dismissive phrases: {total_dismissive // n} (avg per debate: {total_dismissive/n:.1f})")
    print(f"  Strategic rhetoric: {avg_strategic_rhetoric:.2f}")
    
    print("\n" + "="*80)
    
    # Export summary to CSV
    try:
        import csv
        output_file = Path(transcript_directory) / "batch_analysis_summary.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'filename',
                'ideal_speech_score',
                'comprehensibility',
                'truth',
                'truthfulness',
                'rightness',
                'engagement',
                'questions',
                'evidence',
                'acknowledgments',
                'contradictions',
                'dismissive',
                'topic_continuity',
                'strategic_rhetoric'
            ])
            
            # Data rows
            for result in all_results:
                agg = result['aggregates']
                writer.writerow([
                    result['filename'],
                    f"{agg['ideal_speech_adherence_score']:.2f}",
                    f"{agg['avg_comprehensibility']:.2f}",
                    f"{agg['avg_truth']:.2f}",
                    f"{agg['avg_truthfulness']:.2f}",
                    f"{agg['avg_rightness']:.2f}",
                    f"{agg['avg_engagement']:.2f}",
                    agg['total_questions'],
                    agg['total_evidence'],
                    agg['total_acknowledgments'],
                    agg['total_contradictions'],
                    agg['total_dismissive'],
                    f"{agg['avg_topic_continuity']:.2f}",
                    f"{agg['avg_strategic_rhetoric']:.2f}"
                ])
            
            # Average row
            writer.writerow([
                'AVERAGE',
                f"{avg_ideal_speech:.2f}",
                f"{avg_comprehensibility:.2f}",
                f"{avg_truth:.2f}",
                f"{avg_truthfulness:.2f}",
                f"{avg_rightness:.2f}",
                f"{avg_engagement:.2f}",
                f"{total_questions/n:.2f}",
                f"{total_evidence/n:.2f}",
                f"{total_acknowledgments/n:.2f}",
                f"{total_contradictions/n:.2f}",
                f"{total_dismissive/n:.2f}",
                f"{avg_topic_continuity:.2f}",
                f"{avg_strategic_rhetoric:.2f}"
            ])
        
        print(f"✓ Summary exported to: {output_file}")
        
    except Exception as e:
        print(f"Note: Could not export CSV summary: {e}")
    
    print("="*80)


if __name__ == "__main__":
    
    transcript_dir = 'debatewithoutconstraints_transcripts'
    
    if not Path(transcript_dir).exists():
        print(f"Error: Directory '{transcript_dir}' does not exist")
        sys.exit(1)
    
    batch_analyze(transcript_dir)