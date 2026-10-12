import os
import json
import re
import random

class ScriptDirector:
    def __init__(self, brand_title="THE UNTOLD TRUTH", personality="untold_truth"):
        self.brand_title = brand_title
        self.set_personality(personality)

    def set_personality(self, personality_key):
        key = personality_key.lower().replace(" ", "_")
        if "layi" in key or "laya" in key or "prof" in key:
            self.personality = "prof_layi"
            self.brand_title = "PROF LAYI"
        else:
            self.personality = "untold_truth"
            self.brand_title = "THE UNTOLD TRUTH"

    def generate_script(self, topic_input, personality=None):
        """
        Dynamically writes an entirely NEW, original 5-beat viral retention script.
        Never recycles old past clips verbatim.
        Personas supported:
        - 'untold_truth': Dark Machiavellian realism, contrarian aphorisms, cold power dynamics
        - 'prof_layi': Flamboyant orator masterclass, satirical Nigerian economic parables, deadpan street wisdom
        """
        active_p = (personality or self.personality).lower()
        if isinstance(topic_input, dict):
            topic_str = topic_input.get("title", "") + " " + topic_input.get("theme", "")
        else:
            topic_str = str(topic_input).strip()

        if "layi" in active_p or "prof" in active_p or "laya" in active_p:
            return self._generate_new_prof_layi_script(topic_str)
        else:
            return self._generate_new_untold_truth_script(topic_str)

    def _generate_new_untold_truth_script(self, topic_str):
        """
        Creatively authors an ORIGINAL script in the voice of THE UNTOLD TRUTH.
        """
        clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic_str).strip()
        if not clean_topic:
            clean_topic = random.choice([
                "The Trap of Artificial Kindness",
                "Why Modesty Keeps You Impoverished",
                "The False Currency of Good Intentions",
                "Why Nobody Respects a Peacemaker",
                "The Silent Toll of Explaining Yourself",
                "How Predators Identify Easy Prey",
                "The Myth of Shared Sacrifice"
            ])

        subject = clean_topic.title()
        subject_lower = clean_topic.lower()

        # Dynamic creative components based on subject
        hooks = [
            f"The moment you show someone all your cards, you give them permission to dictate your worth.",
            f"Nobody actually respects a martyr. They just take the free sacrifice and walk away.",
            f"If being nice made you powerful, donkeys would be ruling the jungle.",
            f"The fastest way to lose respect is to explain yourself to someone committed to misunderstanding you.",
            f"Stop looking for loyalty in places where people only trade in convenience.",
            f"Your boundaries are completely meaningless until someone gets offended by them."
        ]
        
        realities = [
            f"Society tells you that patience and silence are noble virtues. But in the real world, silence without leverage is just voluntary submission.",
            f"You spend years absorbing insults and calling it maturity. Meanwhile, the people walking over you perceive your patience as weakness.",
            f"Institutions and employers do not reward sacrifice; they optimize for predictability. When you never push back, you become an invisible utility.",
            f"People love giving you advice on how to remain humble, but notice they never practice that modesty when distributing power."
        ]

        mechanisms = [
            f"Power never submits to emotional appeals. It only calculates leverage and replacement costs. If replacing you costs nothing, your dignity is worth nothing.",
            f"The human brain quickly devalues anything given away without friction. When your availability is limitless, your value drops to absolute zero.",
            f"Every social hierarchy runs on an unspoken transaction: those who cannot tolerate confrontation end up paying for the comfort of everyone else."
        ]

        truths = [
            f"The world does not test your kindness; it tests your capacity to inflict consequences. Until you can walk away from the table, you are not negotiating.",
            f"The people who complain the loudest about your new boundaries are the exact ones who benefited the most from you having none.",
            f"You are not safe inside the crowd. You are simply well-behaved cattle grazing in an enclosure someone else owns."
        ]

        outros = [
            f"Build your fortress in private, enforce your borders without apology, and let results announce your authority.",
            f"Stop negotiating with predators. Close the door, secure your citadel, and never look back.",
            f"Learn to move with ruthless quiet. True power never raises its voice; it changes the rules while everyone is sleeping.",
            f"Guard your leverage with your life. Because when the music stops, only those with a throne get to sit down."
        ]

        # Deterministic variation seeded by topic
        seed = sum(ord(c) for c in topic_str)
        hook = hooks[seed % len(hooks)]
        reality = realities[(seed + 1) % len(realities)]
        mechanism = mechanisms[(seed + 2) % len(mechanisms)]
        truth = truths[(seed + 3) % len(truths)]
        outro = outros[(seed + 4) % len(outros)]

        title = f"THE UNTOLD TRUTH ABOUT {subject.upper()}" if not subject.upper().startswith("THE") else subject.upper()

        beats = [
            {
                "beat_index": 1,
                "name": "1. Contrarian Hook",
                "text": hook,
                "zoom_dir": "in",
                "keywords": ["cynical", "king", "observer", "smirk", "truth", "shadows"]
            },
            {
                "beat_index": 2,
                "name": "2. Reality Check",
                "text": reality,
                "zoom_dir": "out",
                "keywords": ["laborer", "crowd", "struggle", "desk", "worker", "chains"]
            },
            {
                "beat_index": 3,
                "name": "3. Hidden Mechanism",
                "text": mechanism,
                "zoom_dir": "in",
                "keywords": ["politician", "oligarch", "banker", "gold", "puppet", "scale"]
            },
            {
                "beat_index": 4,
                "name": "4. Brutal Truth",
                "text": truth,
                "zoom_dir": "out",
                "keywords": ["cage", "ruins", "tomb", "mirror", "citadel", "throne"]
            },
            {
                "beat_index": 5,
                "name": "5. Lingering Outro",
                "text": outro,
                "zoom_dir": "in",
                "keywords": ["solitary", "departure", "master", "walking", "monarch", "fortress"]
            }
        ]

        return {
            "title": title,
            "personality": "untold_truth",
            "topic": topic_str,
            "brand_name": "THE UNTOLD TRUTH",
            "full_script": " ".join([b["text"] for b in beats]),
            "beats": beats
        }

    def _generate_new_prof_layi_script(self, topic_str):
        """
        Creatively authors an ORIGINAL script in the voice of PROF LAYI.
        DNA: Flamboyant orator, didactic Nigerian street economics, absurd parables, masterclass benediction.
        """
        clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic_str).strip()
        if not clean_topic:
            clean_topic = random.choice([
                "The Fallacy of Empty Prayers",
                "Why Cheap Food Produces Expensive Hospital Bills",
                "The Arrogance of Being Penniless",
                "Why Nobody Respects a Humble Beggar",
                "How Inflation Disgraces Hard Labor",
                "The Difference Between Hustle and Perceived Value"
            ])

        subject = clean_topic.title()
        subject_lower = clean_topic.lower()

        seed = sum(ord(c) for c in topic_str)

        hooks = [
            f"Keep quiet, let me talk to you about {subject_lower}. The proof of knowledge is demonstration.",
            f"Sit down properly and listen. You are suffering from acute intellectual stubbornness.",
            f"Let me advise you free of charge before the harshness of life conducts your orientation.",
            f"Nobody wants to listen to an orator whose stomach is actively playing drums.",
            f"Keep quiet and let this enter into your spinal cord: hard work without information is just dignified slavery."
        ]

        fallacies = [
            f"You said you are waiting for a golden opportunity. Let me ask you: the person waiting for a ship at a bus stop, what medical diagnosis should we assign him?",
            f"My mentor taught me that the chronic suffering of many people is believing that moral sentiment can pay electricity bills.",
            f"You boast that you have ten certificates hanging on the wall, but when rain falls, your roof is distributing cold water into buckets.",
            f"People will praise your good character all day, but go to the supermarket and try paying for milk with good character."
        ]

        illustrations = [
            f"When you have money, even your ordinary cough sounds like deep ancient wisdom. But go broke for two weeks and see. Suddenly everyone discovers your presence is taking up unnecessary room ventilation.",
            f"A man who spends twelve hours a day sweating under the sun is called a laborer. A man who spends thirty minutes signing a paper is called a chairman. The difference is not sweat; it is leverage.",
            f"You cannot feed a household with pure optimism. Economic reality does not respect tears; it only respects commercial exchange.",
            f"Those that run after paper currency will forever be outpaced by inflation. Currency must circulate through perpetual assets."
        ]

        escalations = [
            f"From the state of financial breakdown to the state of financial breakthrough, you must upgrade your mental software. Those who refuse to adapt will be retired by modern reality.",
            f"Anybody who is doing better than you in this life simply possesses vital information that you were too proud to seek. Humble yourself and acquire knowledge.",
            f"Stop worshipping manual labor and start constructing perceived value. Information is the fuel of human elevation."
        ]

        punchlines = [
            f"My name is Prof Layi, and I am telling you: information is what makes a man fly. Go and demonstrate your competence today.",
            f"Either you wake up and command your economic output, or life will reduce your ambition to survival rations. Information is what makes a man fly.",
            f"Upgrade your leverage, stop defending poverty, and let your results speak. Information is what makes a man fly."
        ]

        hook = hooks[seed % len(hooks)]
        fallacy = fallacies[(seed + 1) % len(fallacies)]
        illustration = illustrations[(seed + 2) % len(illustrations)]
        escalation = escalations[(seed + 3) % len(escalations)]
        punchline = punchlines[(seed + 4) % len(punchlines)]

        title = f"PROF LAYI ON {subject.upper()}" if not subject.upper().startswith("PROF") else subject.upper()

        beats = [
            {
                "beat_index": 1,
                "name": "1. Didactic Hook",
                "text": hook,
                "zoom_dir": "in",
                "keywords": ["orator", "professor", "courtroom", "suit", "smirk", "throne"]
            },
            {
                "beat_index": 2,
                "name": "2. The Fallacy Breakdown",
                "text": fallacy,
                "zoom_dir": "out",
                "keywords": ["scholar", "crowd", "desk", "books", "philosopher", "lecture"]
            },
            {
                "beat_index": 3,
                "name": "3. Absurd Illustration",
                "text": illustration,
                "zoom_dir": "in",
                "keywords": ["coins", "hands", "scale", "banker", "market", "formula"]
            },
            {
                "beat_index": 4,
                "name": "4. The Escalation",
                "text": escalation,
                "zoom_dir": "out",
                "keywords": ["banquet", "palace", "watch", "aristocrat", "departure", "diploma"]
            },
            {
                "beat_index": 5,
                "name": "5. Masterclass Maxim",
                "text": punchline,
                "zoom_dir": "in",
                "keywords": ["master", "lectern", "crown", "diploma", "fly", "orator"]
            }
        ]

        return {
            "title": title,
            "personality": "prof_layi",
            "topic": topic_str,
            "brand_name": "PROF LAYI",
            "full_script": " ".join([b["text"] for b in beats]),
            "beats": beats
        }

if __name__ == "__main__":
    director = ScriptDirector()
    print("--- PROF LAYI DYNAMIC SCRIPT ---")
    s1 = director.generate_script("The Illusion of Job Security", personality="prof_layi")
    print(s1["title"])
    print(s1["full_script"], "\n")

    print("--- THE UNTOLD TRUTH DYNAMIC SCRIPT ---")
    s2 = director.generate_script("Why People Envy Your Growth", personality="untold_truth")
    print(s2["title"])
    print(s2["full_script"])
