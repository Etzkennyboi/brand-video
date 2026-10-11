import os
import json
import re

TEMPLATES = {
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

class ScriptDirector:
    def __init__(self, brand_title="THE UNTOLD TRUTH"):
        self.brand_title = brand_title

    def generate_script(self, topic_input):
        """
        Generates a 5-beat viral retention script JSON.
        topic_input can be a topic string or dictionary.
        """
        if isinstance(topic_input, dict):
            topic_str = topic_input.get("title", "") + " " + topic_input.get("theme", "")
        else:
            topic_str = str(topic_input)

        topic_lower = topic_str.lower()

        # Match template or adapt
        chosen_key = "loyalty"
        for k in TEMPLATES.keys():
            if k in topic_lower:
                chosen_key = k
                break
        
        # Check additional keywords
        if "corrupt" in topic_lower or "truth" in topic_lower or "theat" in topic_lower:
            chosen_key = "corruption"
        elif "knife" in topic_lower or "betray" in topic_lower or "kingmaker" in topic_lower:
            chosen_key = "kingmaker"
        elif "salary" in topic_lower or "wealth" in topic_lower or "rich" in topic_lower or "comfort" in topic_lower:
            chosen_key = "money"
        elif "silence" in topic_lower or "stoic" in topic_lower or "quiet" in topic_lower:
            chosen_key = "silence"

        data = TEMPLATES[chosen_key]

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
            "topic": topic_str,
            "full_script": full_script,
            "beats": beats
        }

if __name__ == "__main__":
    director = ScriptDirector()
    res = director.generate_script("The Myth of Loyalty at Work")
    print("Script Generated:")
    print(json.dumps(res, indent=2))
