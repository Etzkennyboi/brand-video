import os
import json
import re

# 1. THE UNTOLD TRUTH TEMPLATES (Cynical, Machiavellian, Cold Realism)
UNTOLD_TRUTH_TEMPLATES = {
    "loyalty": {
        "title": "THE LOYALTY TRAP",
        "hook": "Being loyal to a company is the fastest way to get replaced.",
        "reality": "You trade your youth, your evenings, and your health believing loyalty is recorded in some celestial ledger. But the moment revenue dips, your decade of devotion is reduced to a severance check.",
        "mechanism": "Corporations do not reward sacrifice; they exploit predictability. The quiet worker who never complains is not respected—they are utilized. Promotion does not go to the most faithful, but to the most replaceable fear-inducer.",
        "truth": "Your company is an economic entity, not your family. If you dropped dead at your desk on a Tuesday, your position would be posted on LinkedIn by Thursday afternoon.",
        "outro": "Work for your skills, work for your equity, but never surrender your soul for a logo that will forget your name before your grave gets cold."
    },
    "corruption": {
        "title": "THE NATIONAL AUDITION",
        "hook": "People do not actually hate corruption. They just hate that it is not their turn yet.",
        "reality": "If a destitute man steals a loaf in the alley, an angry mob hunts him down without mercy. But when an oligarch embezzles eighty billion from the treasury, his community greets him with chieftaincy titles.",
        "mechanism": "The problem is rarely the leadership alone; it is the culture of survival. The loud activist shouts from the barricades, until they are granted an air-conditioned office and a seat at the banquet.",
        "truth": "The secret dream was never to dismantle the citadel. The secret dream was always to survive long enough to hold the golden ladle.",
        "outro": "Until a people hate the crime more than they envy the criminal, the cycle will repeat forever."
    },
    "kingmaker": {
        "title": "THE KINGMAKER DILEMMA",
        "hook": "Notice who stopped clapping when you started winning.",
        "reality": "People love supporting you when you are struggling because your pain reassures their superiority. They will happily play the mentor while you stay beneath them.",
        "mechanism": "The moment you ascend higher than the pedestal they built for you, their encouragement turns into whispered contempt. A Kingmaker rarely accepts becoming a subject.",
        "truth": "The knife that cuts the deepest is never held by a stranger. It is wielded by the ally who believed they owned your future.",
        "outro": "Build your empire with those who celebrate your throne, not those who demand rent for helping you lay the bricks."
    },
    "money": {
        "title": "THE COMFORT CAGE",
        "hook": "A comfortable salary is the drug employers give you to forget your ambition.",
        "reality": "You tell yourself it is only temporary—just until you pay down the debt, just until you buy the car. But decade by decade, the gilded cage shrinks around you.",
        "mechanism": "The modern system does not shackle your wrists with iron; it sedates your mind with convenience, direct deposits, and subscription entertainment.",
        "truth": "You are not safe. You are merely well-fed livestock inside an economic pasture designed to harvest your prime years.",
        "outro": "Either build your own vessel today, or spend your entire life rowing someone else's galleon into the sunset."
    },
    "silence": {
        "title": "THE POWER OF SILENCE",
        "hook": "The loudest person in the room is always the most insecure.",
        "reality": "Weakness announces itself with noise, bragging, and desperate demands for applause. True power sits in the corner, observing everything and revealing nothing.",
        "mechanism": "When you speak too much, you hand your enemies the blueprint to destroy you. Information given away for free is leverage you will never regain.",
        "truth": "The master strategist never explains his moves. He lets the result speak while his competitors scramble to understand what hit them.",
        "outro": "Learn to move in absolute silence. Surprise is the ultimate weapon."
    }
}

# 2. SIR ROGERS TEMPLATES (Cheeky Exploit Analyst, Game Theory, Simulation & Loopholes)
SIR_ROGERS_TEMPLATES = {
    "casino": {
        "title": "HOW CASINOS TRICK YOUR BRAIN",
        "hook": "You're a casino owner, and you have a problem. People don't like losing their money to you. Here's how you fix it.",
        "mechanism_1": "Take down all the clocks, block out the windows, and rearrange your floor to have a maze-like layout. Now their sense of time and direction starts to blur.",
        "mechanism_2": "Next, the critical move: replace real money with chips. It is so much harder to track how much you're down when it is just abstract colored tokens.",
        "escalation": "Before they leave, hand them free drinks. Now they feel valued, and alcohol isn't exactly famous for improving risk management. When they lose big, stop them and hand them a shiny VIP loyalty card.",
        "punchline": "They are now premium customers eligible for free hotel suites. And all they had to do was lose their entire paycheck."
    },
    "martingale": {
        "title": "THE DOUBLE OR NOTHING TRAP",
        "hook": "You just bet ten dollars on red and lost it. Fortunately, some guru online told you about a guaranteed win strategy.",
        "mechanism_1": "Each time you lose, you just double the bet. So to recoup that ten bucks, you bet twenty. Still lose. Now to regain that, you bet forty. Ah, tough luck. Eighty. So close. One-sixty.",
        "mechanism_2": "You have never seen a black streak so long. Surely it can't go for any longer. Your previous bet was twelve hundred dollars.",
        "escalation": "So to recoup that loss, you dig into your life savings and bet your final twenty-five hundred dollars. You're in too deep to stop now. The bets are locked.",
        "punchline": "The dealer spins the wheel, and this is exactly what goes wrong when you follow the Martingale betting trap."
    },
    "slot_machine": {
        "title": "THE MOST ADDICTIVE MACHINE",
        "hook": "Your job is to design the most addictive slot machine in history. Here is how you do it.",
        "mechanism_1": "First, when a player loses, make sure it is a near miss. Studies show the human brain reacts to near misses similarly to actual wins. It feels frustrating, but it forces us to keep pulling.",
        "mechanism_2": "Second, disguise losses as wins. If they bet a dollar and hit point five, they didn't lose fifty cents. They won fifty cents. Celebrate it with bright lights, sounds, and animations.",
        "escalation": "Lastly, make it fast. This is not roulette where you wait between spins. Pack in as many spins per minute as possible until they enter a betting-induced trance.",
        "punchline": "Congrats. You just designed the most profitable casino game in human history."
    },
    "billionaire_bet": {
        "title": "THE BILLIONAIRE AIRLINE BET",
        "hook": "Two billionaire friends who were rival airline owners agreed to a crazy bet with their egos on the line.",
        "mechanism_1": "They both owned competing airlines and Formula One racing teams. So they agreed: whoever's team finishes last has to dress as a female flight attendant and serve drinks on the winner's airline.",
        "mechanism_2": "When Richard Branson's team came last, he kept his word. He shaved his legs, kept his beard, put on lipstick, heels, and the full rival uniform.",
        "escalation": "He did the safety demo and served drinks. But while serving juice, he realized the passenger was Tony Fernandez, the rival he lost the bet to. So naturally, he accidentally dumped an entire tray of orange juice right onto his lap.",
        "punchline": "Tony spent the rest of the flight in his underwear on his own airplane. Man, if I'm ever rich, I want to be like these guys."
    },
    "illegal_gambling": {
        "title": "THE STREET TRIVIA TRAP",
        "hook": "If an influencer comes up to you in the street offering five bucks to answer trivia, don't answer too fast. You might be committing a felony.",
        "mechanism_1": "Under lottery laws, an illegal gambling game requires three elements: prize, chance, and consideration. That means risking something of value for a chance-based reward.",
        "mechanism_2": "If you ever flip a coin to decide who pays for dinner, that technically could be unlicensed gambling. Or playing credit card roulette where the waiter randomly selects whose card pays for the whole group.",
        "escalation": "A street influencer is usually just a giveaway since you don't put money on the line. But what if you answer correctly, and then he looks you in the eye with a grin?",
        "punchline": "And says: Do you want to go double or nothing?"
    },
    "scam_reversal": {
        "title": "HOW SCAMMERS SCAMMED THE POLITICIANS",
        "hook": "Who could fall for some silly scam like the Nigerian prince fraud? Well, actually, some Nigerian politicians.",
        "mechanism_1": "When advance-fee email scams exploded, causing nearly a billion dollars in losses, the government launched an anti-corruption commission to hunt the fraudsters.",
        "mechanism_2": "However, this completely backfired. Scammers did something genius. Instead of targeting random foreigners, they posed as federal investigators and sent letters to corrupt politicians.",
        "escalation": "They told the politicians they had proof of their illegal bribes, but would kill the investigation for a fee. Out of pure paranoia, guilty officials rushed to comply.",
        "punchline": "Raking in millions of dollars by using the politicians' own guilty secrets against them."
    },
    "betting_delay": {
        "title": "THE ONE-SECOND DELAY HUSTLE",
        "hook": "It's not easy to fool a multi-billion dollar betting company, but this might be the dumbest way to try.",
        "mechanism_1": "In live sports betting, you can wager on events in real-time. Problem is, when someone scores, there is a one to two second delay before the bookie updates the digital system.",
        "mechanism_2": "So bettors buy tickets, sit in the stadium, and try to mash the button the split-second the ball crosses the line. Except spotters in the arena will kick you out if they catch you on your phone.",
        "escalation": "The workaround? Pop in an AirPod, call your buddy at home, and yell 'Let's go, they scored!' while he places the bet from his sofa.",
        "punchline": "Except bookmaker algorithms detect abnormal latency patterns in milliseconds, and they freeze your account before you can cash out."
    }
}

# 3. PROF LAYI TEMPLATES (Satirical Faux-Intellectual Wisdom, Legalistic Oratory, Absurd Realities)
PROF_LAYI_TEMPLATES = {
    "accomplishment": {
        "title": "NOBODY ACCOMPANIES THE UNACCOMPLISHED",
        "hook": "Keep quiet, let me talk to you. Nobody wants to accompany who is not accomplished.",
        "fallacy": "You said your partner left you because the economy is harsh. Let me ask you: the person who told you love does not cost a dime, was he paying house rent with affection?",
        "illustration": "When you have money, even your ordinary cough sounds like deep ancient wisdom. But go broke for two weeks and see. Suddenly everyone discovers your presence is taking up unnecessary room ventilation.",
        "escalation": "Fly business class to London and see if you will meet your childhood friends who refused to adapt. The size of your balance sheet determines the radius of your loyal entourage.",
        "punchline": "Become accomplished first, and you will see that accompaniment is completely free of charge. Information is what makes a man fly."
    },
    "mathematician": {
        "title": "THE MATHEMATICIAN'S DILEMMA",
        "hook": "You say money cannot solve all your problems. Good. But neither can mathematics.",
        "fallacy": "Last week, my mathematician friend called me to borrow twenty thousand naira to buy baby formula. If a senior mathematician cannot feed a toddler with calculus, why are you doing simple addition?",
        "illustration": "Hard work pays, but it pays minimum wage. That is why billionaires do not work to chase currency; they work to construct perceived value.",
        "escalation": "Anybody who is more successful than you simply possesses vital information that you have not humbled yourself to seek. Without information, you are running in circles.",
        "punchline": "Stop trying to calculate your way out of poverty. Upgrade your economic output, or your baby will be drinking pure water instead of formula."
    },
    "demonstration": {
        "title": "THE PROOF OF KNOWLEDGE",
        "hook": "The proof of knowledge is demonstration. Keep quiet and let that sink into your marrow.",
        "fallacy": "My mentor taught me that the chronic suffering of humanity is the fallacy of thinking: 'I could do it if I wanted to.' But until you do it and finish it, nobody knows that you know it.",
        "illustration": "You are not a master cobbler until you produce a shoe that does not fall apart before the owner reaches the street corner.",
        "escalation": "Ancient Greek philosophers conceived grand thoughts, but they did not settle hospital bills with contemplation. Do not confuse your temporary destination with your ultimate destiny.",
        "punchline": "Adaptation is the true mark of intelligence. Either demonstrate your competence today, or retire quietly into intellectual arrogance."
    },
    "currency": {
        "title": "WHY CURRENCY MUST BE CURRENT",
        "hook": "Money was never designed to sit in one place. That is why it is called currency.",
        "fallacy": "Currency must be current. If water ceases to flow, it becomes a breeding ground for mosquitoes. If your capital ceases to circulate, it becomes emotional baggage.",
        "illustration": "You boast that you have kept two million naira under your mattress for ten years. Meanwhile, inflation has downgraded your life savings to the price of two bags of rice.",
        "escalation": "Those who run after paper money cannot run a sustainable enterprise. The wealthy understand that cash is merely an instrument to acquire perpetual leverage.",
        "punchline": "Keep your capital moving, upgrade your knowledge constantly, and stop worshipping paper that loses value while you are asleep."
    },
    "matrimony": {
        "title": "MATRIMONY WITHOUT MONEY",
        "hook": "Let me advise you free of charge: any matrimony without money is a magic trick.",
        "fallacy": "When you are broke and heartbroken simultaneously, do not arrange a pity party. Take it as an avenue for a breakthrough, not an emotional breakdown.",
        "illustration": "Every mother, every sister, and every wife respects the law of the stomach. Love is sweet, but nobody cooks jollof rice with romantic poetry.",
        "escalation": "From the state of financial breakdown to the state of financial breakthrough, you must establish independent economic power.",
        "punchline": "My name is Prof Layi, and I am telling you: balance your economic ledger before you propose to someone's daughter."
    },
    "wristwatch": {
        "title": "THE FORTY-THREE MILLION NAIRA WATCH",
        "hook": "Do not listen to the financial advice of unaccomplished men.",
        "fallacy": "One of my mentors bought a wristwatch for forty-three million naira. A spectator asked him: 'Sir, does that watch tell you different time from a wall clock?'",
        "illustration": "He smiled and replied: 'I did not buy this watch to tell the time. I bought it to dictate the time of whoever sits across my desk.'",
        "escalation": "Overthinkers do not have enough time to take action, and overdoers do not have enough time to think. Analysis without capital is just an academic funeral.",
        "punchline": "Know your worth, position your leverage, and remember that perception is ninety percent of market reality."
    }
}

class ScriptDirector:
    def __init__(self, brand_title="THE UNTOLD TRUTH", personality="untold_truth"):
        self.brand_title = brand_title
        self.set_personality(personality)

    def set_personality(self, personality_key):
        key = personality_key.lower().replace(" ", "_")
        if "layi" in key or "laya" in key or "prof" in key:
            self.personality = "prof_layi"
            self.brand_title = "PROF LAYI"
        elif "roger" in key:
            self.personality = "sir_rogers"
            self.brand_title = "SIR ROGERS"
        else:
            self.personality = "untold_truth"
            self.brand_title = "THE UNTOLD TRUTH"

    def generate_script(self, topic_input, personality=None):
        """
        Generates a 5-beat viral retention script tailored to the chosen personality:
        - 'untold_truth': Cynical, Machiavellian, philosophical power realism
        - 'prof_layi': Deadpan satirical wisdom, legalistic proverbs, GNCC masterclass orator
        - 'sir_rogers': Cheeky exploit analyst, game theory, simulation hooks, behavioral mechanics
        """
        active_personality = personality or self.personality
        if isinstance(topic_input, dict):
            topic_str = topic_input.get("title", "") + " " + topic_input.get("theme", "")
        else:
            topic_str = str(topic_input)

        topic_lower = topic_str.lower()

        if "layi" in active_personality.lower() or "laya" in active_personality.lower() or "prof" in active_personality.lower():
            return self._generate_prof_layi_script(topic_str, topic_lower)
        elif "roger" in active_personality.lower():
            return self._generate_sir_rogers_script(topic_str, topic_lower)
        else:
            return self._generate_untold_truth_script(topic_str, topic_lower)

    def _generate_sir_rogers_script(self, topic_str, topic_lower):
        # Match built-in Sir Rogers samples
        chosen_key = "casino"
        if "martingale" in topic_lower or "double" in topic_lower or "red" in topic_lower or "streak" in topic_lower:
            chosen_key = "martingale"
        elif "slot" in topic_lower or "machine" in topic_lower or "addict" in topic_lower:
            chosen_key = "slot_machine"
        elif "billionaire" in topic_lower or "rival" in topic_lower or "branson" in topic_lower or "bet" in topic_lower:
            chosen_key = "billionaire_bet"
        elif "trivia" in topic_lower or "influencer" in topic_lower or "illegal" in topic_lower or "lottery" in topic_lower:
            chosen_key = "illegal_gambling"
        elif "nigerian" in topic_lower or "scam" in topic_lower or "fraud" in topic_lower or "politician" in topic_lower:
            chosen_key = "scam_reversal"
        elif "delay" in topic_lower or "sports" in topic_lower or "airpod" in topic_lower or "bookie" in topic_lower:
            chosen_key = "betting_delay"
        elif "casino" in topic_lower or "chip" in topic_lower or "trap" in topic_lower or "money" in topic_lower:
            chosen_key = "casino"
        else:
            # Dynamic Sir Rogers generation for ANY custom topic
            clean_subject = re.sub(r'[^a-zA-Z0-9\s]', '', topic_str).strip().title()
            return self._synthesize_dynamic_sir_rogers(clean_subject)

        data = SIR_ROGERS_TEMPLATES[chosen_key]
        beats = [
            {
                "beat_index": 1,
                "name": "1. POV Simulation Hook",
                "text": data["hook"],
                "zoom_dir": "in",
                "keywords": ["casino", "banker", "player", "bet", "cards", "gold"]
            },
            {
                "beat_index": 2,
                "name": "2. The Tactical Exploit",
                "text": data["mechanism_1"],
                "zoom_dir": "out",
                "keywords": ["clock", "window", "maze", "roulette", "crowd", "chips"]
            },
            {
                "beat_index": 3,
                "name": "3. The Psychological Mechanism",
                "text": data["mechanism_2"],
                "zoom_dir": "in",
                "keywords": ["coins", "scale", "hands", "exchange", "lights", "trance"]
            },
            {
                "beat_index": 4,
                "name": "4. Escalation & Trap",
                "text": data["escalation"],
                "zoom_dir": "out",
                "keywords": ["vip", "drinks", "airpod", "phone", "banquet", "loss"]
            },
            {
                "beat_index": 5,
                "name": "5. Cheeky Punchline / Wrap-up",
                "text": data["punchline"],
                "zoom_dir": "in",
                "keywords": ["smirk", "throne", "jackpot", "trophy", "congrats", "master"]
            }
        ]

        full_script = " ".join([b["text"] for b in beats])
        return {
            "title": data["title"],
            "personality": "sir_rogers",
            "topic": topic_str,
            "full_script": full_script,
            "beats": beats
        }

    def _synthesize_dynamic_sir_rogers(self, subject):
        """
        Dynamically crafts a script in Sir Rogers' exact DNA for any custom subject.
        DNA: Second-person POV roleplay -> Exploit 1 -> Cognitive bias manipulation -> VIP Escalation -> Cheeky punchline.
        """
        title = f"THE TRUTH ABOUT {subject.upper()}"
        hook = f"You run a {subject.lower()} empire, and you have a problem. Customers don't like handing over their hard-earned money. Here is how you fix it."
        mech_1 = f"First, alter the perception of value. Make the process fast, effortless, and wrapped in warm design. Now their rational decision-making starts to blur."
        mech_2 = f"Second, the critical step: disguise the actual cost behind abstract tokens and subscriptions. Studies show it is ten times harder to notice loss when it feels like frictionless membership."
        escalation = f"And just when they realize the trap and want to cancel, stop them right there and offer a shiny loyalty perk. Now they feel valued, and they double down on the very thing draining them."
        punchline = f"Congrats. You just designed the most profitable business loophole in modern history."

        beats = [
            {"beat_index": 1, "name": "1. POV Simulation Hook", "text": hook, "zoom_dir": "in", "keywords": ["banker", "courtier", "gold", "smirk", "deal"]},
            {"beat_index": 2, "name": "2. The Tactical Exploit", "text": mech_1, "zoom_dir": "out", "keywords": ["architect", "blueprint", "palace", "crowd"]},
            {"beat_index": 3, "name": "3. The Psychological Mechanism", "text": mech_2, "zoom_dir": "in", "keywords": ["coins", "hands", "scale", "deed"]},
            {"beat_index": 4, "name": "4. Escalation & Trap", "text": escalation, "zoom_dir": "out", "keywords": ["aristocrat", "banquet", "wine", "exchange"]},
            {"beat_index": 5, "name": "5. Cheeky Punchline / Wrap-up", "text": punchline, "zoom_dir": "in", "keywords": ["throne", "crown", "master", "departure"]}
        ]
        return {
            "title": title,
            "personality": "sir_rogers",
            "topic": subject,
            "full_script": " ".join([b["text"] for b in beats]),
            "beats": beats
        }

    def _generate_prof_layi_script(self, topic_str, topic_lower):
        chosen_key = "accomplishment"
        if "accomplish" in topic_lower or "accompany" in topic_lower or "friend" in topic_lower or "london" in topic_lower:
            chosen_key = "accomplishment"
        elif "math" in topic_lower or "formula" in topic_lower or "calculat" in topic_lower or "billionaire" in topic_lower or "poverty" in topic_lower:
            chosen_key = "mathematician"
        elif "demonstrat" in topic_lower or "knowledge" in topic_lower or "proof" in topic_lower or "shoe" in topic_lower or "destin" in topic_lower:
            chosen_key = "demonstration"
        elif "curren" in topic_lower or "flow" in topic_lower or "mattress" in topic_lower or "infla" in topic_lower:
            chosen_key = "currency"
        elif "matrimon" in topic_lower or "marry" in topic_lower or "wife" in topic_lower or "husband" in topic_lower or "break" in topic_lower or "heart" in topic_lower or "love" in topic_lower:
            chosen_key = "matrimony"
        elif "watch" in topic_lower or "time" in topic_lower or "wrist" in topic_lower or "million" in topic_lower or "overthink" in topic_lower:
            chosen_key = "wristwatch"
        elif "money" in topic_lower or "wealth" in topic_lower or "broke" in topic_lower:
            chosen_key = "currency"
        else:
            clean_subject = re.sub(r'[^a-zA-Z0-9\s]', '', topic_str).strip().title()
            return self._synthesize_dynamic_prof_layi(clean_subject)

        data = PROF_LAYI_TEMPLATES[chosen_key]
        beats = [
            {
                "beat_index": 1,
                "name": "1. Didactic Hook",
                "text": data["hook"],
                "zoom_dir": "in",
                "keywords": ["orator", "professor", "courtroom", "suit", "smirk", "throne"]
            },
            {
                "beat_index": 2,
                "name": "2. The Fallacy Breakdown",
                "text": data["fallacy"],
                "zoom_dir": "out",
                "keywords": ["scholar", "crowd", "desk", "books", "philosopher", "lecture"]
            },
            {
                "beat_index": 3,
                "name": "3. Absurd Illustration",
                "text": data["illustration"],
                "zoom_dir": "in",
                "keywords": ["coins", "hands", "scale", "banker", "market", "formula"]
            },
            {
                "beat_index": 4,
                "name": "4. The Escalation",
                "text": data["escalation"],
                "zoom_dir": "out",
                "keywords": ["banquet", "palace", "watch", "aristocrat", "departure", "diploma"]
            },
            {
                "beat_index": 5,
                "name": "5. Masterclass Maxim",
                "text": data["punchline"],
                "zoom_dir": "in",
                "keywords": ["master", "lectern", "crown", "diploma", "fly", "orator"]
            }
        ]

        full_script = " ".join([b["text"] for b in beats])
        return {
            "title": data["title"],
            "personality": "prof_layi",
            "topic": topic_str,
            "full_script": full_script,
            "beats": beats
        }

    def _synthesize_dynamic_prof_layi(self, subject):
        """
        Dynamically crafts a script in Prof Layi's exact DNA for any custom subject.
        DNA: Didactic Hook ('Keep quiet, let me talk to you') -> Fallacy Breakdown ->
        Absurd Mathematician / Baby Formula Illustration -> Escalation -> Masterclass Maxim ('Information is what makes a man fly').
        """
        title = f"PROF LAYI ON {subject.upper()}"
        hook = f"Keep quiet, let me talk to you about {subject.lower()}. The proof of knowledge is demonstration."
        fallacy = f"My mentor once taught me that the chronic suffering of humanity is the intellectual arrogance of assuming {subject.lower()} can be sustained on passion alone."
        illustration = f"You say you have deep passion, but last week my mathematician called me to borrow twenty thousand naira for baby formula. Passion without economic output is merely a well-rehearsed delusion."
        escalation = f"Anybody who has truly mastered {subject.lower()} possesses vital information that you have not yet humbled yourself to acquire. Currency must be current, and value must be demonstrated."
        punchline = f"From the state of financial breakdown to the state of financial breakthrough. Ask me why? Because information is what makes a man fly."

        beats = [
            {"beat_index": 1, "name": "1. Didactic Hook", "text": hook, "zoom_dir": "in", "keywords": ["orator", "professor", "courtroom", "suit", "smirk", "throne"]},
            {"beat_index": 2, "name": "2. The Fallacy Breakdown", "text": fallacy, "zoom_dir": "out", "keywords": ["scholar", "crowd", "desk", "books", "philosopher"]},
            {"beat_index": 3, "name": "3. Absurd Illustration", "text": illustration, "zoom_dir": "in", "keywords": ["coins", "hands", "scale", "banker", "formula"]},
            {"beat_index": 4, "name": "4. The Escalation", "text": escalation, "zoom_dir": "out", "keywords": ["banquet", "palace", "watch", "aristocrat", "departure"]},
            {"beat_index": 5, "name": "5. Masterclass Maxim", "text": punchline, "zoom_dir": "in", "keywords": ["master", "lectern", "crown", "diploma", "fly"]}
        ]
        return {
            "title": title,
            "personality": "prof_layi",
            "topic": subject,
            "full_script": " ".join([b["text"] for b in beats]),
            "beats": beats
        }

    def _generate_untold_truth_script(self, topic_str, topic_lower):
        chosen_key = "loyalty"
        for k in UNTOLD_TRUTH_TEMPLATES.keys():
            if k in topic_lower:
                chosen_key = k
                break
        
        if "corrupt" in topic_lower or "truth" in topic_lower or "theat" in topic_lower:
            chosen_key = "corruption"
        elif "knife" in topic_lower or "betray" in topic_lower or "kingmaker" in topic_lower:
            chosen_key = "kingmaker"
        elif "salary" in topic_lower or "wealth" in topic_lower or "rich" in topic_lower or "comfort" in topic_lower:
            chosen_key = "money"
        elif "silence" in topic_lower or "stoic" in topic_lower or "quiet" in topic_lower:
            chosen_key = "silence"

        data = UNTOLD_TRUTH_TEMPLATES[chosen_key]
        beats = [
            {
                "beat_index": 1,
                "name": "1. Contrarian Hook",
                "text": data["hook"],
                "zoom_dir": "in",
                "keywords": ["hook", "cynical", "king", "observer", "smirk", "truth"]
            },
            {
                "beat_index": 2,
                "name": "2. Reality Check",
                "text": data["reality"],
                "zoom_dir": "out",
                "keywords": ["laborer", "chains", "crowd", "struggle", "desk", "worker"]
            },
            {
                "beat_index": 3,
                "name": "3. Hidden Mechanism",
                "text": data["mechanism"],
                "zoom_dir": "in",
                "keywords": ["politician", "oligarch", "banker", "gold", "puppet", "scheming"]
            },
            {
                "beat_index": 4,
                "name": "4. Brutal Truth",
                "text": data["truth"],
                "zoom_dir": "out",
                "keywords": ["cage", "grave", "ruins", "tomb", "shadows", "mirror"]
            },
            {
                "beat_index": 5,
                "name": "5. Lingering Outro",
                "text": data["outro"],
                "zoom_dir": "in",
                "keywords": ["spoon", "throne", "solitary", "departure", "master", "walking"]
            }
        ]

        full_script = " ".join([b["text"] for b in beats])
        return {
            "title": data["title"],
            "personality": "untold_truth",
            "topic": topic_str,
            "full_script": full_script,
            "beats": beats
        }

if __name__ == "__main__":
    director = ScriptDirector(personality="sir_rogers")
    print("--- SIR ROGERS SAMPLE ---")
    s = director.generate_script("casino")
    print(f"Title: {s['title']}")
    print(f"Script: {s['full_script']}\n")

    print("--- DYNAMIC SIR ROGERS TOPIC ---")
    d = director.generate_script("Gym Memberships")
    print(f"Title: {d['title']}")
    print(f"Script: {d['full_script']}\n")

    print("--- UNTOLD TRUTH SAMPLE ---")
    u = director.generate_script("loyalty", personality="untold_truth")
    print(f"Title: {u['title']}")
    print(f"Script: {u['full_script']}")
