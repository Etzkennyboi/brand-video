import os
import json
import re

# 1. THE UNTOLD TRUTH EXEMPLAR SEEDS (Cynical, Machiavellian, Cold Realism)
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

# 2. PROF LAYI EXEMPLAR SEEDS (Satirical Faux-Intellectual Wisdom, Legalistic Oratory, Absurd Realities)
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
        else:
            self.personality = "untold_truth"
            self.brand_title = "THE UNTOLD TRUTH"

    def generate_script(self, topic_input, personality=None):
        """
        Generates a 5-beat viral retention script tailored to the chosen personality:
        - 'untold_truth': Cynical, Machiavellian, philosophical power realism
        - 'prof_layi': Deadpan satirical wisdom, legalistic proverbs, GNCC masterclass orator
        """
        active_personality = personality or self.personality
        if isinstance(topic_input, dict):
            topic_str = topic_input.get("title", "") + " " + topic_input.get("theme", "")
        else:
            topic_str = str(topic_input)

        topic_lower = topic_str.lower()

        if "layi" in active_personality.lower() or "laya" in active_personality.lower() or "prof" in active_personality.lower():
            return self._generate_prof_layi_script(topic_str, topic_lower)
        else:
            return self._generate_untold_truth_script(topic_str, topic_lower)

    def _synthesize_dynamic_prof_layi(self, subject):
        """
        Dynamically crafts a script in Prof Layi's exact DNA for any custom subject.
        DNA: Didactic Hook ('Keep quiet, let me talk to you') -> Fallacy Breakdown ->
        Absurd Mathematician / Economic Illustration -> Escalation -> Masterclass Maxim ('Information is what makes a man fly').
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

    def _generate_prof_layi_script(self, topic_str, topic_lower):
        chosen_key = None
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
        
        if not chosen_key:
            clean_subject = re.sub(r'[^a-zA-Z0-9\s]', '', topic_str).strip().title()
            return self._synthesize_dynamic_prof_layi(clean_subject)

        data = PROF_LAYI_TEMPLATES[chosen_key]
        beats = [
            {"beat_index": 1, "name": "1. Didactic Hook", "text": data["hook"], "zoom_dir": "in", "keywords": ["orator", "professor", "courtroom", "suit", "smirk", "throne"]},
            {"beat_index": 2, "name": "2. The Fallacy Breakdown", "text": data["fallacy"], "zoom_dir": "out", "keywords": ["scholar", "crowd", "desk", "books", "philosopher", "lecture"]},
            {"beat_index": 3, "name": "3. Absurd Illustration", "text": data["illustration"], "zoom_dir": "in", "keywords": ["coins", "hands", "scale", "banker", "market", "formula"]},
            {"beat_index": 4, "name": "4. The Escalation", "text": data["escalation"], "zoom_dir": "out", "keywords": ["banquet", "palace", "watch", "aristocrat", "departure", "diploma"]},
            {"beat_index": 5, "name": "5. Masterclass Maxim", "text": data["punchline"], "zoom_dir": "in", "keywords": ["master", "lectern", "crown", "diploma", "fly", "orator"]}
        ]

        full_script = " ".join([b["text"] for b in beats])
        return {
            "title": data["title"],
            "personality": "prof_layi",
            "topic": topic_str,
            "full_script": full_script,
            "beats": beats
        }

    def _synthesize_dynamic_untold_truth(self, subject):
        """
        Dynamically crafts a script in The Untold Truth's cynical Machiavellian DNA.
        """
        title = f"THE TRUTH ABOUT {subject.upper()}"
        hook = f"Nobody actually respects your loyalty to {subject.lower()}. They only respect what they cannot replace."
        reality = f"Society teaches you that {subject.lower()} is a noble sacrifice. But in reality, institutions treat your devotion as a predictable discount on your true worth."
        mechanism = f"Power does not negotiate with sentimentality; it yields only to scarcity. When you give away your energy without leverage, you are not valued—you are consumed."
        truth = f"The moment you become inconvenient to their balance sheet, the very people cheering you today will replace you without hesitation."
        outro = f"Stop building shrines to people who view you as temporary scaffolding. Build your own leverage, or remain a spectator to your own life."

        beats = [
            {"beat_index": 1, "name": "1. Contrarian Hook", "text": hook, "zoom_dir": "in", "keywords": ["king", "observer", "smirk", "throne", "shadows"]},
            {"beat_index": 2, "name": "2. Reality Check", "text": reality, "zoom_dir": "out", "keywords": ["laborer", "chains", "crowd", "struggle", "desk"]},
            {"beat_index": 3, "name": "3. Hidden Mechanism", "text": mechanism, "zoom_dir": "in", "keywords": ["politician", "oligarch", "banker", "gold", "puppet"]},
            {"beat_index": 4, "name": "4. Brutal Truth", "text": truth, "zoom_dir": "out", "keywords": ["cage", "grave", "ruins", "tomb", "mirror"]},
            {"beat_index": 5, "name": "5. Lingering Outro", "text": outro, "zoom_dir": "in", "keywords": ["solitary", "departure", "master", "walking", "monument"]}
        ]
        return {
            "title": title,
            "personality": "untold_truth",
            "topic": subject,
            "full_script": " ".join([b["text"] for b in beats]),
            "beats": beats
        }

    def _generate_untold_truth_script(self, topic_str, topic_lower):
        chosen_key = None
        for k in UNTOLD_TRUTH_TEMPLATES.keys():
            if k in topic_lower:
                chosen_key = k
                break
        
        if "corrupt" in topic_lower or "theat" in topic_lower:
            chosen_key = "corruption"
        elif "knife" in topic_lower or "betray" in topic_lower or "kingmaker" in topic_lower:
            chosen_key = "kingmaker"
        elif "salary" in topic_lower or "wealth" in topic_lower or "rich" in topic_lower or "comfort" in topic_lower:
            chosen_key = "money"
        elif "silence" in topic_lower or "stoic" in topic_lower or "quiet" in topic_lower:
            chosen_key = "silence"
        elif "loyalty" in topic_lower or "work" in topic_lower or "job" in topic_lower:
            chosen_key = "loyalty"

        if not chosen_key:
            clean_subject = re.sub(r'[^a-zA-Z0-9\s]', '', topic_str).strip().title()
            return self._synthesize_dynamic_untold_truth(clean_subject)

        data = UNTOLD_TRUTH_TEMPLATES[chosen_key]
        beats = [
            {"beat_index": 1, "name": "1. Contrarian Hook", "text": data["hook"], "zoom_dir": "in", "keywords": ["hook", "cynical", "king", "observer", "smirk", "truth"]},
            {"beat_index": 2, "name": "2. Reality Check", "text": data["reality"], "zoom_dir": "out", "keywords": ["laborer", "chains", "crowd", "struggle", "desk", "worker"]},
            {"beat_index": 3, "name": "3. Hidden Mechanism", "text": data["mechanism"], "zoom_dir": "in", "keywords": ["politician", "oligarch", "banker", "gold", "puppet", "scheming"]},
            {"beat_index": 4, "name": "4. Brutal Truth", "text": data["truth"], "zoom_dir": "out", "keywords": ["cage", "grave", "ruins", "tomb", "shadows", "mirror"]},
            {"beat_index": 5, "name": "5. Lingering Outro", "text": data["outro"], "zoom_dir": "in", "keywords": ["spoon", "throne", "solitary", "departure", "master", "walking"]}
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
    director = ScriptDirector(personality="untold_truth")
    print("Testing Untold Truth dynamic generation...")
    u = director.generate_script("The Scam of Gym Memberships")
    print(f"Title: {u['title']}")
    print(f"Hook: {u['beats'][0]['text']}")
    print(f"Script: {u['full_script']}\n")

    print("Testing Prof Layi dynamic generation...")
    l = director.generate_script("Cryptocurrency Trading", personality="prof_layi")
    print(f"Title: {l['title']}")
    print(f"Hook: {l['beats'][0]['text']}")
    print(f"Script: {l['full_script']}")
