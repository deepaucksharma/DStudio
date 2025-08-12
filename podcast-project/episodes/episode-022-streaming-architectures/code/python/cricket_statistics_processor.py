"""
Cricket Statistics Real-time Stream Processor
यह system IPL match के दौरान real-time cricket statistics calculate करता है
Example: Strike rates, bowling figures, team comparisons, player milestones
"""

import json
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import threading
import queue
from kafka import KafkaConsumer, KafkaProducer
import statistics
import redis

@dataclass
class CricketBall:
    """हर ball की information के लिए data structure"""
    match_id: str
    over: int
    ball: int
    batsman: str
    bowler: str
    runs: int
    is_wicket: bool
    wicket_type: str = ""
    fielder: str = ""
    is_boundary: bool = False
    is_six: bool = False
    is_wide: bool = False
    is_noball: bool = False
    is_bye: bool = False
    is_legbye: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    commentary: str = ""

@dataclass 
class PlayerStats:
    """Player के real-time statistics"""
    name: str
    runs: int = 0
    balls_faced: int = 0
    fours: int = 0
    sixes: int = 0
    strike_rate: float = 0.0
    is_out: bool = False
    out_type: str = ""
    
    # Bowling stats
    overs_bowled: float = 0.0
    runs_conceded: int = 0
    wickets: int = 0
    economy_rate: float = 0.0
    balls_bowled: int = 0

@dataclass
class TeamStats:
    """Team के real-time statistics"""
    name: str
    runs: int = 0
    wickets: int = 0
    overs: float = 0.0
    run_rate: float = 0.0
    balls_faced: int = 0
    boundaries: int = 0
    sixes: int = 0
    extras: int = 0

class CricketStatisticsProcessor:
    """
    Real-time cricket statistics processing engine
    Mumbai local train की speed से cricket data process करता है!
    """
    
    def __init__(self, kafka_servers: str = "localhost:9092", redis_host: str = "localhost"):
        self.kafka_servers = kafka_servers
        self.redis_client = redis.Redis(host=redis_host, port=6379, decode_responses=True)
        
        # Data structures for statistics
        self.player_stats: Dict[str, PlayerStats] = {}
        self.team_stats: Dict[str, TeamStats] = {}
        self.match_state = {}
        self.over_summaries = {}
        self.partnerships = []
        self.current_partnership = {"batsmen": [], "runs": 0, "balls": 0, "start_over": 0}
        
        # Threading और queues
        self.processing_queue = queue.Queue(maxsize=10000)
        self.is_running = False
        
        # Mumbai-style constants
        self.BOUNDARY_RUNS = [4, 6]
        self.POWERPLAY_OVERS = 6
        self.DEATH_OVERS_START = 16
        
        print("🏏 Cricket Statistics Processor initialize हो गया!")
    
    def setup_kafka_consumer(self) -> KafkaConsumer:
        """Kafka consumer setup करते हैं ball-by-ball data के लिए"""
        consumer = KafkaConsumer(
            'ipl-live-scores',
            bootstrap_servers=[self.kafka_servers],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='cricket-stats-processor',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        print("📡 Kafka consumer ready for cricket data")
        return consumer
    
    def setup_kafka_producer(self) -> KafkaProducer:
        """Statistics publish करने के लिए producer"""
        producer = KafkaProducer(
            bootstrap_servers=[self.kafka_servers],
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8')
        )
        return producer
    
    def process_ball_data(self, ball_data: Dict) -> CricketBall:
        """Raw ball data को CricketBall object में convert करते हैं"""
        ball = CricketBall(
            match_id=ball_data.get('matchId', ''),
            over=ball_data.get('over', 0),
            ball=ball_data.get('ball', 0),
            batsman=ball_data.get('batsman', ''),
            bowler=ball_data.get('bowler', ''),
            runs=ball_data.get('runs', 0),
            is_wicket=ball_data.get('isWicket', False),
            wicket_type=ball_data.get('wicketType', ''),
            fielder=ball_data.get('fielder', ''),
            commentary=ball_data.get('commentary', '')
        )
        
        # Extras और boundaries determine करते हैं
        ball.is_boundary = ball.runs == 4
        ball.is_six = ball.runs == 6
        ball.is_wide = 'wide' in ball.commentary.lower()
        ball.is_noball = 'no ball' in ball.commentary.lower()
        
        return ball
    
    def update_player_batting_stats(self, ball: CricketBall):
        """Batsman के statistics update करते हैं"""
        if ball.batsman not in self.player_stats:
            self.player_stats[ball.batsman] = PlayerStats(ball.batsman)
        
        player = self.player_stats[ball.batsman]
        
        # Basic batting stats
        if not ball.is_wide and not ball.is_noball:
            player.balls_faced += 1
        
        # Runs (बल्लेबाज़ के account में तभी जाएंगे जब वो खुद खेले हों)
        if not ball.is_bye and not ball.is_legbye:
            player.runs += ball.runs
        
        # Boundaries count करते हैं
        if ball.is_boundary:
            player.fours += 1
        elif ball.is_six:
            player.sixes += 1
        
        # Strike rate calculate करते हैं
        if player.balls_faced > 0:
            player.strike_rate = (player.runs * 100) / player.balls_faced
        
        # Wicket information
        if ball.is_wicket and ball.batsman in ball.commentary:
            player.is_out = True
            player.out_type = ball.wicket_type
    
    def update_player_bowling_stats(self, ball: CricketBall):
        """Bowler के statistics update करते हैं"""
        if ball.bowler not in self.player_stats:
            self.player_stats[ball.bowler] = PlayerStats(ball.bowler)
        
        bowler = self.player_stats[ball.bowler]
        
        # Bowling stats
        if not ball.is_wide and not ball.is_noball:
            bowler.balls_bowled += 1
        
        # Runs conceded (सिर्फ़ bowler के account में जाने वाले runs)
        if not ball.is_bye and not ball.is_legbye:
            bowler.runs_conceded += ball.runs
        
        # Wickets
        if ball.is_wicket:
            bowler.wickets += 1
        
        # Overs calculation
        bowler.overs_bowled = bowler.balls_bowled / 6.0
        
        # Economy rate
        if bowler.overs_bowled > 0:
            bowler.economy_rate = bowler.runs_conceded / bowler.overs_bowled
    
    def update_team_stats(self, ball: CricketBall, batting_team: str):
        """Team के overall statistics update करते हैं"""
        if batting_team not in self.team_stats:
            self.team_stats[batting_team] = TeamStats(batting_team)
        
        team = self.team_stats[batting_team]
        
        # Team runs में सब कुछ add होता है
        team.runs += ball.runs
        
        # Balls faced
        if not ball.is_wide and not ball.is_noball:
            team.balls_faced += 1
        
        # Wickets
        if ball.is_wicket:
            team.wickets += 1
        
        # Boundaries और sixes
        if ball.is_boundary:
            team.boundaries += 1
        elif ball.is_six:
            team.sixes += 1
        
        # Extras
        if ball.is_wide or ball.is_noball or ball.is_bye or ball.is_legbye:
            team.extras += ball.runs
        
        # Overs और run rate
        team.overs = team.balls_faced / 6.0
        if team.overs > 0:
            team.run_rate = team.runs / team.overs
    
    def update_partnership_stats(self, ball: CricketBall):
        """Current partnership के stats update करते हैं"""
        if ball.batsman not in self.current_partnership["batsmen"]:
            if len(self.current_partnership["batsmen"]) >= 2:
                # New partnership शुरू हो गई
                self.partnerships.append(self.current_partnership.copy())
                self.current_partnership = {
                    "batsmen": [ball.batsman],
                    "runs": 0,
                    "balls": 0,
                    "start_over": ball.over
                }
            else:
                self.current_partnership["batsmen"].append(ball.batsman)
        
        # Partnership में runs add करते हैं
        if not ball.is_bye and not ball.is_legbye:
            self.current_partnership["runs"] += ball.runs
        
        if not ball.is_wide and not ball.is_noball:
            self.current_partnership["balls"] += 1
        
        # अगर wicket गिरी तो partnership ख़त्म
        if ball.is_wicket:
            self.partnerships.append(self.current_partnership.copy())
            self.current_partnership = {
                "batsmen": [],
                "runs": 0,
                "balls": 0,
                "start_over": ball.over
            }
    
    def calculate_advanced_statistics(self, ball: CricketBall) -> Dict:
        """Advanced cricket statistics calculate करते हैं"""
        stats = {}
        
        # Current run rate vs required run rate
        if ball.match_id in self.team_stats:
            team = list(self.team_stats.values())[0]  # Batting team
            
            # Powerplay statistics
            if ball.over <= self.POWERPLAY_OVERS:
                stats["powerplay_runs"] = team.runs
                stats["powerplay_run_rate"] = team.run_rate
                stats["powerplay_wickets"] = team.wickets
            
            # Death overs statistics
            if ball.over >= self.DEATH_OVERS_START:
                # Death overs का data calculate करना होगा
                stats["death_overs_phase"] = True
                stats["pressure_index"] = self.calculate_pressure_index(ball)
        
        # Partnership analysis
        if self.current_partnership["balls"] > 0:
            partnership_run_rate = (self.current_partnership["runs"] * 6) / self.current_partnership["balls"]
            stats["current_partnership"] = {
                "batsmen": self.current_partnership["batsmen"],
                "runs": self.current_partnership["runs"],
                "balls": self.current_partnership["balls"],
                "run_rate": partnership_run_rate
            }
        
        # Player milestones check करते हैं
        milestones = self.check_milestones(ball)
        if milestones:
            stats["milestones"] = milestones
        
        return stats
    
    def calculate_pressure_index(self, ball: CricketBall) -> float:
        """
        Pressure index calculate करते हैं
        Mumbai traffic जैसे - kitna pressure hai batting team पर
        """
        if ball.match_id not in self.match_state:
            return 0.0
        
        # Required run rate, wickets left, overs left के हिसाब से pressure
        team = list(self.team_stats.values())[0]
        overs_left = 20 - team.overs
        wickets_left = 10 - team.wickets
        
        if overs_left <= 0 or wickets_left <= 0:
            return 10.0  # Maximum pressure
        
        # Target के हिसाब से required rate
        # यहाँ example के लिए 180 runs target assume कर रहे हैं
        target = 180
        required_runs = target - team.runs
        required_rate = required_runs / overs_left if overs_left > 0 else 0
        
        current_rate = team.run_rate
        rate_difference = max(0, required_rate - current_rate)
        
        # Pressure formula
        pressure = (rate_difference * 2) + (10 - wickets_left) + (max(0, 4 - overs_left) * 0.5)
        return min(10.0, pressure)  # Cap at 10
    
    def check_milestones(self, ball: CricketBall) -> List[Dict]:
        """Player milestones check करते हैं"""
        milestones = []
        
        if ball.batsman in self.player_stats:
            player = self.player_stats[ball.batsman]
            
            # Batting milestones
            if player.runs == 50:
                milestones.append({
                    "type": "HALF_CENTURY",
                    "player": ball.batsman,
                    "runs": 50,
                    "balls": player.balls_faced,
                    "description": f"{ball.batsman} का अर्धशतक!"
                })
            elif player.runs == 100:
                milestones.append({
                    "type": "CENTURY", 
                    "player": ball.batsman,
                    "runs": 100,
                    "balls": player.balls_faced,
                    "description": f"{ball.batsman} का शतक!"
                })
        
        # Bowling milestones
        if ball.bowler in self.player_stats:
            bowler = self.player_stats[ball.bowler]
            if bowler.wickets == 3:
                milestones.append({
                    "type": "HAT_TRICK_CHANCE",
                    "player": ball.bowler,
                    "wickets": 3,
                    "description": f"{ball.bowler} के पास hat-trick का मौका!"
                })
        
        return milestones
    
    def publish_statistics(self, producer: KafkaProducer, ball: CricketBall, advanced_stats: Dict):
        """Calculated statistics को Kafka में publish करते हैं"""
        
        # Player statistics
        player_data = {
            "type": "PLAYER_STATS",
            "match_id": ball.match_id,
            "timestamp": datetime.now().isoformat(),
            "players": {name: {
                "runs": p.runs,
                "balls_faced": p.balls_faced,
                "strike_rate": round(p.strike_rate, 2),
                "fours": p.fours,
                "sixes": p.sixes,
                "is_out": p.is_out
            } for name, p in self.player_stats.items() if p.balls_faced > 0 or p.balls_bowled > 0}
        }
        
        # Team statistics  
        team_data = {
            "type": "TEAM_STATS",
            "match_id": ball.match_id,
            "timestamp": datetime.now().isoformat(),
            "teams": {name: {
                "runs": t.runs,
                "wickets": t.wickets,
                "overs": round(t.overs, 1),
                "run_rate": round(t.run_rate, 2),
                "boundaries": t.boundaries,
                "sixes": t.sixes,
                "extras": t.extras
            } for name, t in self.team_stats.items()}
        }
        
        # Advanced statistics
        advanced_data = {
            "type": "ADVANCED_STATS",
            "match_id": ball.match_id,
            "timestamp": datetime.now().isoformat(),
            "stats": advanced_stats
        }
        
        # Kafka में publish करते हैं
        producer.send('cricket-player-stats', value=player_data)
        producer.send('cricket-team-stats', value=team_data)
        producer.send('cricket-advanced-stats', value=advanced_data)
        
        # Redis में भी cache करते हैं fast access के लिए
        self.cache_to_redis(ball.match_id, player_data, team_data, advanced_data)
    
    def cache_to_redis(self, match_id: str, player_data: Dict, team_data: Dict, advanced_data: Dict):
        """Redis में statistics cache करते हैं"""
        try:
            # Set with expiry (2 hours)
            self.redis_client.setex(f"match:{match_id}:players", 7200, json.dumps(player_data))
            self.redis_client.setex(f"match:{match_id}:teams", 7200, json.dumps(team_data))
            self.redis_client.setex(f"match:{match_id}:advanced", 7200, json.dumps(advanced_data))
            
            # Live score के लिए simple key भी रखते हैं
            if self.team_stats:
                team = list(self.team_stats.values())[0]
                live_score = f"{team.runs}/{team.wickets} ({team.overs} overs)"
                self.redis_client.setex(f"live:{match_id}", 7200, live_score)
                
        except Exception as e:
            print(f"❌ Redis cache error: {str(e)}")
    
    def print_live_summary(self, ball: CricketBall):
        """Console में live summary print करते हैं"""
        print("\n" + "="*80)
        print(f"🏏 LIVE CRICKET STATS - Over {ball.over}.{ball.ball}")
        print("="*80)
        
        # Team stats
        for team_name, team in self.team_stats.items():
            print(f"🏏 {team_name}: {team.runs}/{team.wickets} ({team.overs:.1f} overs, RR: {team.run_rate:.2f})")
        
        # Current partnership
        if self.current_partnership["batsmen"]:
            batsmen = " & ".join(self.current_partnership["batsmen"])
            partnership_rr = (self.current_partnership["runs"] * 6 / self.current_partnership["balls"]) if self.current_partnership["balls"] > 0 else 0
            print(f"🤝 Current Partnership: {batsmen} - {self.current_partnership['runs']} runs in {self.current_partnership['balls']} balls (RR: {partnership_rr:.2f})")
        
        # Key players
        print("\n📊 KEY PLAYERS:")
        for name, player in self.player_stats.items():
            if player.balls_faced > 0:
                print(f"🏏 {name}: {player.runs} ({player.balls_faced}b, SR: {player.strike_rate:.1f}) - {player.fours}×4, {player.sixes}×6")
            elif player.balls_bowled > 0:
                overs = f"{player.balls_bowled//6}.{player.balls_bowled%6}"
                print(f"⚾ {name}: {player.overs_bowled:.1f}-0-{player.runs_conceded}-{player.wickets} (Eco: {player.economy_rate:.2f})")
        
        print("="*80)
    
    def process_streaming_data(self):
        """Main processing loop - continuous cricket data processing"""
        consumer = self.setup_kafka_consumer()
        producer = self.setup_kafka_producer()
        
        print("🚀 Cricket statistics processing शुरू हो गई...")
        self.is_running = True
        
        try:
            for message in consumer:
                if not self.is_running:
                    break
                
                # Ball data process करते हैं
                ball_data = message.value
                ball = self.process_ball_data(ball_data)
                
                # Default batting team (production में यह message से आएगा)
                batting_team = ball_data.get('battingTeam', 'Team A')
                
                # सभी statistics update करते हैं
                self.update_player_batting_stats(ball)
                self.update_player_bowling_stats(ball)
                self.update_team_stats(ball, batting_team)
                self.update_partnership_stats(ball)
                
                # Advanced stats calculate करते हैं
                advanced_stats = self.calculate_advanced_statistics(ball)
                
                # Results publish करते हैं
                self.publish_statistics(producer, ball, advanced_stats)
                
                # Live summary display
                if ball.ball % 6 == 0 or ball.is_wicket:  # Every over या wicket पर
                    self.print_live_summary(ball)
                
        except KeyboardInterrupt:
            print("\n🛑 Processing को stop कर रहे हैं...")
        except Exception as e:
            print(f"❌ Processing error: {str(e)}")
        finally:
            self.is_running = False
            consumer.close()
            producer.close()
            print("✅ Cricket Statistics Processor बंद हो गया")
    
    def get_match_summary(self, match_id: str) -> Dict:
        """Complete match summary return करता है"""
        try:
            # Redis से cached data ले रहे हैं
            player_data = self.redis_client.get(f"match:{match_id}:players")
            team_data = self.redis_client.get(f"match:{match_id}:teams")
            advanced_data = self.redis_client.get(f"match:{match_id}:advanced")
            
            summary = {}
            if player_data:
                summary["players"] = json.loads(player_data)
            if team_data:
                summary["teams"] = json.loads(team_data)
            if advanced_data:
                summary["advanced"] = json.loads(advanced_data)
            
            summary["partnerships"] = self.partnerships
            summary["generated_at"] = datetime.now().isoformat()
            
            return summary
            
        except Exception as e:
            print(f"❌ Error getting match summary: {str(e)}")
            return {}

def create_sample_cricket_data():
    """Testing के लिए sample cricket data generate करते हैं"""
    from kafka import KafkaProducer
    import random
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    # Sample players
    batsmen = ["Rohit Sharma", "Virat Kohli", "MS Dhoni", "Hardik Pandya", "KL Rahul"]
    bowlers = ["Jasprit Bumrah", "Yuzvendra Chahal", "Deepak Chahar", "Bhuvneshwar Kumar"]
    
    match_id = "MI_vs_CSK_IPL_Final_2024"
    batting_team = "Mumbai Indians"
    bowling_team = "Chennai Super Kings"
    
    total_runs = 0
    wickets = 0
    
    print("🏏 Generating sample cricket data...")
    
    try:
        for over in range(1, 21):  # 20 overs
            for ball in range(1, 7):  # 6 balls per over
                
                # Random ball outcome
                runs = random.choices([0, 1, 2, 3, 4, 6], weights=[30, 25, 20, 10, 10, 5])[0]
                is_wicket = random.choice([True, False]) if runs == 0 else False
                is_wicket = is_wicket and random.random() < 0.1  # 10% wicket chance on dot balls
                
                total_runs += runs
                if is_wicket:
                    wickets += 1
                
                # Commentary generate करते हैं
                commentary = f"{runs} runs"
                if runs == 4:
                    commentary = f"FOUR! Beautiful shot by {random.choice(batsmen)}"
                elif runs == 6:
                    commentary = f"SIX! {random.choice(batsmen)} ने stands में भेज दिया!"
                elif is_wicket:
                    commentary = f"WICKET! {random.choice(batsmen)} OUT!"
                
                ball_data = {
                    "matchId": match_id,
                    "battingTeam": batting_team,
                    "bowlingTeam": bowling_team,
                    "over": over,
                    "ball": ball,
                    "batsman": random.choice(batsmen),
                    "bowler": random.choice(bowlers),
                    "runs": runs,
                    "isWicket": is_wicket,
                    "wicketType": "caught" if is_wicket else "",
                    "totalRuns": total_runs,
                    "wicketsDown": wickets,
                    "commentary": commentary,
                    "timestamp": datetime.now().isoformat()
                }
                
                producer.send('ipl-live-scores', value=ball_data)
                
                print(f"Over {over}.{ball}: {commentary} (Total: {total_runs}/{wickets})")
                
                time.sleep(2)  # 2 seconds delay between balls
                
                if wickets >= 10:  # All out
                    break
            
            if wickets >= 10:
                break
        
        producer.flush()
        print(f"✅ Sample match data generated! Final Score: {total_runs}/{wickets}")
        
    except Exception as e:
        print(f"❌ Error generating sample data: {str(e)}")
    finally:
        producer.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-data":
        create_sample_cricket_data()
    else:
        processor = CricketStatisticsProcessor()
        processor.process_streaming_data()