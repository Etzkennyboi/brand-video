import os
import json
import random
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CATALOG = os.path.join(ROOT_DIR, "assets", "visual_vault", "catalog.json")
DEFAULT_IMAGES = os.path.join(ROOT_DIR, "assets", "visual_vault", "images")

# Option A: Comprehensive 100-Image Metaphorical Vault Catalog
# Maps every dark-renaissance oil painting in the vault to its allegorical and symbolic meanings.
IMAGE_METAPHORS = {
    "Aging_king_smirking_in_shadows.jpg": ["power", "cynical", "ruler", "shadows", "smirk", "experience", "leverage", "knowing", "unmoved", "king", "observer", "control", "truth", "monarch"],
    "Antique_brass_key_on_deed.jpg": ["ownership", "deed", "property", "asset", "title", "landlord", "equity", "key", "contract", "unlock", "wealth", "security", "real estate"],
    "Architect_reviewing_parchment_bl_.jpg": ["blueprint", "plan", "design", "structure", "architect", "strategy", "foundation", "drafting", "building", "preparation", "cathedral"],
    "Architects_quarreling_near_unfin_.jpg": ["quarrel", "committee", "argument", "confusion", "infighting", "delay", "excuses", "debate", "bickering", "unfinished", "bureaucracy"],
    "Aristocratic_courtier_bowing_wit_.jpg": ["courtier", "bowing", "subservience", "sycophant", "yes man", "pleasing", "flattery", "explaining", "apology", "polite lie", "obedience"],
    "Aristocratic_woman_posing_in_velvet.jpg": ["status", "luxury", "vanity", "velvet", "appearance", "prestige", "glamour", "privilege", "poise", "impression", "fashion"],
    "Aristocrats_dancing_in_Baroque_b_.jpg": ["distraction", "entertainment", "shallow", "party", "ballroom", "dance", "celebration", "heedless", "oblivious", "pleasure"],
    "Aristocrats_looking_from_balcony.jpg": ["elites", "spectator", "detachment", "looking down", "superiority", "distance", "balcony", "unreachable", "hierarchy"],
    "Armored_guard_looking_at_torches.jpg": ["defense", "guard", "security", "protection", "barrier", "night watch", "armor", "vigilance", "gate", "boundaries"],
    "Audience_member_clapping_with_te_.jpg": ["applause", "clapping", "approval", "validation", "crowd", "seeking praise", "tears", "cheering", "audience", "spectator"],
    "Banker_counting_gold_bars.jpg": ["banker", "gold", "capital", "wealth", "counting", "finance", "money", "profit", "balance sheet", "rich", "treasury", "interest", "debt", "cash"],
    "Beggar_boy_watching_banquet.jpg": ["poverty", "excluded", "inequality", "hunger", "outsider", "looking in", "beggar", "scarcity", "deprived", "envy", "have nots", "broke"],
    "Bishops_counting_gold_coins.jpg": ["hypocrisy", "greed", "holy greed", "bishops", "institution", "hidden money", "morality for sale", "dogma", "corrupt", "church"],
    "Blacksmith_striking_steel_on_anvil.jpg": ["hard work", "labor", "grind", "sweat", "blacksmith", "anvil", "hammer", "effort", "overtime", "brute force", "worker", "toil", "forging", "hammer"],
    "Bound_man_smiling_at_camera.jpg": ["denial", "delusion", "trapped", "coping", "fake happiness", "bound", "hostage", "enduring", "helpless", "smiling through pain"],
    "Boy_removing_armor_holding_sling.jpg": ["agility", "slingshot", "outsmarting", "shedding burden", "underdog", "smart move", "david", "simplicity", "leverage"],
    "Broken_balance_scale_on_floor.jpg": ["unfair", "rigged", "broken system", "injustice", "broken scale", "collapse", "inequality", "tilted", "sham"],
    "Bureaucrats_loading_gold_onto_ca_.jpg": ["taxes", "extraction", "bureaucracy", "siphoning", "moving wealth", "corporate greed", "taking a cut", "middleman", "drain"],
    "Citizens_holding_golden_masks_in_.jpg": ["masks", "fake society", "conformity", "hiding", "deception", "two faced", "hypocrisy", "social pressure", "pretending", "facade"],
    "Coins_tip_scales_of_justice.jpg": ["bought justice", "money talks", "corruption", "scales", "influence", "bribe", "legal sham", "tilted balance", "wealthy advantage"],
    "Commanders_plotting_over_war_map.jpg": ["strategy", "war room", "tactics", "master plan", "coordination", "chess", "calculated risk", "command", "war map", "moves"],
    "Comrades_toasting_across_banquet_.jpg": ["fake friends", "drinking buddies", "fair weather", "banquet", "toasting", "cheers", "complacency", "allies", "drinking"],
    "Courtier_lowering_carnival_mask.jpg": ["revealing truth", "unmasking", "ulterior motives", "hidden intent", "carnival", "deception", "betrayal", "secret", "facade"],
    "Crowd_member_holding_rock.jpg": ["mob", "hypocrite", "throwing stones", "critic", "public shaming", "cancel", "outrage", "judgmental", "troll", "blame", "rock"],
    "Drawbridge_pulling_up_castle_moat.jpg": ["boundaries", "shutting out", "defense", "isolation", "saying no", "drawbridge", "moat", "protecting energy", "fortress", "cutting off"],
    "Elderly_aristocrat_sitting_in_chair.jpg": ["old money", "patience", "established", "sitting back", "passive", "observer", "heritage", "waiting", "unbothered"],
    "Elites_moving_miniature_golden_s_.jpg": ["manipulation", "puppeteer", "moving pieces", "shadow rulers", "orchestration", "hidden hands", "system design", "chess"],
    "Evangelist_holding_Bible_with_gl_.jpg": ["dogma", "preaching", "moral superiority", "lecturing", "unsolicited advice", "guilt tripping", "virtue signaling", "ideology"],
    "Exhausted_soldier_watching_carri_.jpg": ["burnout", "exhaustion", "class divide", "working poor", "tired", "left behind", "carriage", "unfair labor", "fatigue", "drained"],
    "Figure_holding_gold_soup_ladle.jpg": ["spoils", "golden ladle", "looting", "greed", "feeding ego", "gluttony", "privilege", "skimming top", "entitlement"],
    "Figure_rising_from_smoky_ruins.jpg": ["phoenix", "resilience", "rebirth", "rising", "surviving", "ruins", "ashes", "rebuilding", "unbroken", "comeback", "tough"],
    "Gatekeeper_permitting_wealthy_pe_.jpg": ["gatekeeper", "pay to play", "exclusive club", "buying entry", "access", "bribery", "privilege pass", "filtering", "doors"],
    "Gentleman_carrying_gifts_behind__.jpg": ["hidden motives", "bribes", "favors with strings", "gifts", "manipulation", "debt trap", "obligations", "transactional"],
    "Gladiator_catching_breath_in_cat_.jpg": ["performer fatigue", "performing for crowds", "arena", "catching breath", "exhausted", "fighting for applause", "blood sweat"],
    "Gold_coin_on_palm.jpg": ["price tag", "transaction", "payment", "single coin", "handout", "cost", "buying", "selling", "value", "worth"],
    "Golden_throne_in_abandoned_hall.jpg": ["empty title", "fleeting fame", "lonely top", "abandoned power", "vanity", "ruins of pride", "meaningless status", "throne"],
    "Hands_exchanging_goblet_of_wine.jpg": ["poisoned chalice", "temptation", "compromise", "deal with devil", "toast", "pact", "seduction", "dangerous gift", "wine"],
    "Hands_holding_wooden_mug.jpg": ["modest life", "humble", "simple", "working class", "tavern", "basic", "contentment", "grounded", "ordinary"],
    "Hands_manipulating_figures_with__.jpg": ["strings attached", "puppeteer", "manipulation", "controlled", "chess pieces", "hidden leverage", "marionette"],
    "Holding_collection_bag_toward_widow.jpg": ["extortion", "guilt", "taking from poor", "scam", "grift", "fake charity", "exploiting weak", "collection", "religious scam"],
    "Juror_crossing_arms_with_pipe.jpg": ["judgment", "skepticism", "scrutiny", "unimpressed", "jury", "evaluating", "critical eye", "doubt", "arms crossed"],
    "King_Solomon_judging_disputed_in_.jpg": ["tough decision", "wisdom", "dispute", "discernment", "judgment", "ruling", "resolving conflict", "truth seeking"],
    "King_walking_past_cloaked_woman.jpg": ["ignoring distraction", "focus", "walking past", "royalty", "unmoved", "priorities", "cold resolve", "blind to sentiment"],
    "Knight_walking_past_crown.jpg": ["walking away", "refusing crown", "integrity", "rejecting status", "freedom over power", "renouncing", "true nobility", "knight"],
    "Lone_figure_facing_crowd.jpg": ["standing alone", "defiance", "against the tide", "non conformist", "bravery", "outnumbered", "facing mob", "truth teller"],
    "Man_and_woman_at_table.jpg": ["negotiation", "relationship", "matrimony", "dialogue", "tension", "discussion", "expectations", "partnership", "marriage"],
    "Man_dining_alone_in_library.jpg": ["solitude", "peace", "comfortable alone", "library", "intellect", "quiet dinner", "no drama", "sovereign", "independent"],
    "Man_drinking_whiskey_reading_book.jpg": ["studying", "whiskey", "reading", "reflection", "deep work", "night reading", "learning", "knowledge", "calm"],
    "Man_escaping_seductive_queen.jpg": ["escaping trap", "avoiding temptation", "breaking free", "saying no", "resisting seduction", "fleeing", "clarity"],
    "Man_gazing_into_cracked_mirrors.jpg": ["broken identity", "cracked mirror", "self doubt", "fragmented ego", "introspection", "shattered reputation", "reflection"],
    "Man_holding_letter_and_match.jpg": ["burning bridges", "evidence destroyed", "cutting ties", "match", "no turning back", "secret letter", "closing chapter"],
    "Man_resting_in_armchair.jpg": ["peace of mind", "rest", "unbothered", "armchair", "comfortable silence", "relaxation", "letting go", "detachment"],
    "Man_sipping_scotch_in_office.jpg": ["calculated calm", "executive", "after hours", "contemplation", "strategy", "office", "composed", "mastery"],
    "Man_walking_down_cobblestone_street.jpg": ["walking away", "solitary path", "exit", "leaving behind", "cobblestone", "quiet walk", "independence", "moving on"],
    "Man_working_by_candlelight.jpg": ["late night", "grind", "midnight oil", "solitary work", "candlelight", "focus", "discipline", "craftsman", "writing"],
    "Masked_executioner_holding_blade.jpg": ["consequence", "execution", "axe falling", "grim reality", "blade", "inevitable end", "karma", "punishment", "harsh truth"],
    "Master_whispering_to_apprentice.jpg": ["mentorship", "whispered advice", "insider knowledge", "apprentice", "guidance", "teaching", "secret recipe", "influence"],
    "Men_walking_toward_precipice.jpg": ["lemmings", "blind following", "edge of cliff", "precipice", "mass delusion", "herd mentality", "disaster ahead", "blind"],
    "Merchants_counting_profits_in_te_.jpg": ["commerce", "profit", "traders", "counting money", "market", "hustle", "revenue", "business deals", "exchange"],
    "Mob_cornering_man_in_alley.jpg": ["cornered", "cancel culture", "mob attack", "alley", "pressured", "targeted", "witch hunt", "peer pressure", "hostile"],
    "Mob_member_shouting_in_torchlight.jpg": ["mob rage", "shouting", "torchlight", "outrage", "hysteria", "loud critics", "noise", "angry crowd"],
    "Monarch_reclining_on_throne.jpg": ["effortless power", "untouchable", "reclining", "throne", "ruling", "monarch", "leisure", "supremacy", "confidence"],
    "Monk_making_eye_contact.jpg": ["inner peace", "stoic gaze", "unfazed", "monk", "spiritual clarity", "direct truth", "piercing eye", "detachment"],
    "Muscular_warrior_bound_to_pillar.jpg": ["wasted talent", "bound by duty", "enslaved warrior", "tied down", "pillar", "chains", "obligation", "heavy burden", "stuck worker", "horse"],
    "Noble_playing_chess_in_library.jpg": ["chess", "strategy", "calculated move", "patience", "playing ahead", "library", "intellectual game", "tactics", "foresight", "moves"],
    "Noble_sitting_in_mud.jpg": ["fall from grace", "humiliation", "sitting in mud", "bankruptcy", "lost status", "rock bottom", "pride crushed", "ruin", "mud"],
    "Nobleman_tearing_treaty_over_hearth.jpg": ["breaking contract", "tearing treaty", "betrayal", "burning agreements", "void", "breach", "no loyalty", "hearth"],
    "Nobles_carrying_treasure_through_.jpg": ["fleeing capital", "offshore", "saving wealth", "secret treasure", "escape", "moving assets", "pragmatic greed"],
    "Nobles_embracing_while_concealin_.jpg": ["backstab", "dagger behind back", "fake friend", "hug with knife", "treachery", "betrayal", "hidden blade", "ulterior motive"],
    "Noblewoman_looking_into_mirror.jpg": ["vanity", "reputation", "mirror", "self image", "obsession with looks", "perception", "ego", "fragile pride"],
    "Noblewoman_reviewing_suitor_resumes.jpg": ["vetting", "high standards", "filtering", "interviewing", "evaluating suitors", "screening", "selection", "resumes"],
    "Oligarch_at_banquet_portrait.jpg": ["oligarch", "gluttony", "corrupt wealth", "banquet", "plenty", "indulgence", "fat cat", "excess", "plutocrat"],
    "Oligarch_receiving_beaded_crown.jpg": ["coronation", "bought title", "beaded crown", "oligarch", "new money power", "ceremony", "climbing top"],
    "Palace_seneschal_blocking_doorway.jpg": ["gatekeeper", "blocking door", "access denied", "bureaucrat", "palace guard", "permission", "locked out"],
    "Philosopher_holding_coin_portrait.jpg": ["academic theory", "theorist", "philosopher with coin", "hypocritical wisdom", "talk is cheap", "intellectual", "coin"],
    "Politician_pointing_finger_in_panic.jpg": ["deflection", "blame shifting", "pointing finger", "panic", "caught lying", "politician", "excuse", "scapegoat"],
    "Politician_receiving_blessing_in_.jpg": ["holy alliance", "political theater", "fake blessing", "endorsement", "spectacle", "legitimacy show"],
    "Politicians_dueling_with_wooden__.jpg": ["political theater", "fake fight", "wooden swords", "circus", "distraction", "orchestrated feud", "staged conflict"],
    "Preacher_holding_basket_with_coins.jpg": ["religious hustle", "basket with coins", "selling salvation", "grifter", "profiting from faith", "empty promises"],
    "Priest_baptizing_oligarch_with_w_.jpg": ["washing sins", "whitewashing", "pr cleansing", "money laundering", "bought forgiveness", "absolution"],
    "Prisoner_in_cage_in_court.jpg": ["prisoner", "cage", "trapped", "courtroom", "systemic trap", "convicted", "confinement", "guilty", "justice machinery"],
    "Queen_walking_from_palace_gate.jpg": ["leaving palace", "stepping down", "independence", "moving forward", "queen walking", "dignity", "graceful exit"],
    "Queen_wearing_golden_crown_portrait.jpg": ["crown", "queen", "regal", "authority", "poise", "sovereignty", "status", "golden crown"],
    "Relatives_weeping_at_open_tomb.jpg": ["mortality", "grave", "tomb", "what remains", "grief", "relatives", "too late", "legacy", "funeral", "death"],
    "Scholar_holding_quill_at_desk.jpg": ["scholar", "credentials", "degrees", "quill", "academic", "theory over action", "desk worker", "studying", "rules"],
    "Seraphim_guarding_golden_gates.jpg": ["divine gate", "highest standard", "unforgiving standard", "guarding gates", "holy barrier", "sacred boundary"],
    "Silhouettes_gazing_at_golden_cit_.jpg": ["golden city", "distant dream", "aspiration", "elusive wealth", "mirage", "silhouettes", "longing", "ideal"],
    "Silver_coins_tumbling_onto_table.jpg": ["silver coins", "thirty pieces of silver", "payout", "bribe", "transactional loyalty", "price of betrayal", "coins"],
    "Socrates_reaching_for_poison_cup.jpg": ["cheap advice", "poison cup", "poisonous opinion", "dying for bad ideas", "socrates", "hemlock", "fatal dogma", "sacrifice"],
    "Statesman_gazing_from_castle_window.jpg": ["strategic perspective", "window", "observing below", "statesman", "bird eye view", "calm observation", "patience"],
    "Statue_cracking_open_from_heat.jpg": ["cracking under pressure", "breaking point", "facade collapsing", "statue cracking", "false god", "fall of idol", "fragility"],
    "Traveler_standing_at_road_fork.jpg": ["crossroads", "decision point", "two paths", "choice", "fork in road", "traveler", "dilemma", "turning point"],
    "Two_figures_shaking_hands.jpg": ["handshake", "agreement", "pact", "deal", "partnership", "compromise", "mutual interest", "alliance"],
    "Veteran_general_holding_ceremoni_.jpg": ["past glory", "war hero", "ceremonial", "retired glory", "outdated fighter", "veteran", "decorations", "nostalgia"],
    "Warlord_chuckles_with_priest.jpg": ["unholy alliance", "cynical collusion", "warlord and priest", "laughing at masses", "power sharing", "cartel"],
    "Woman_holding_wine_glass.jpg": ["composed", "wine glass", "observing chaos", "poised", "detachment", "sipping wine", "amused", "calm"],
    "Woman_looking_out_carriage_window.jpg": ["looking out", "moving forward", "carriage window", "reflection", "leaving past", "traveling", "melancholy"],
    "Woman_sitting_in_golden_birdcage.jpg": ["golden cage", "gilded cage", "salary trap", "comfortable prison", "luxury trap", "high income slave", "golden handcuffs", "trapped"],
    "Woman_smiling_with_diamond_necklace.jpg": ["diamond necklace", "bought smile", "glamour", "materialism", "wealth display", "trophy", "costly grace"],
    "Wooden_cart_burning_in_square.jpg": ["burning cart", "chaos", "public disaster", "ruined venture", "loss of livelihood", "smoke", "failed enterprise"]
}

# Thematic Concept Thesaurus for Semantic Expansion
THEME_EXPANSION = {
    # Explanation, silence, strategy
    "explain": ["courtier", "bowing", "subservience", "pleasing", "apology", "chess", "silence", "strategy"],
    "explaining": ["courtier", "bowing", "subservience", "pleasing", "apology", "chess", "silence"],
    "justifies": ["courtier", "bowing", "subservience", "pleasing", "justifying"],
    "justifying": ["courtier", "bowing", "subservience", "pleasing", "justifying"],
    "guilt": ["courtier", "bowing", "collection", "extortion", "prisoner"],
    "silence": ["chess", "statesman", "window", "shadows", "quiet", "monk", "cobblestone"],
    "quiet": ["chess", "statesman", "window", "library", "solitude", "cobblestone"],
    "strategist": ["chess", "commanders", "war map", "blueprint", "architect"],
    "strategy": ["chess", "commanders", "war map", "blueprint", "architect"],
    "moves": ["chess", "commanders", "board", "tactics"],
    "move": ["chess", "commanders", "board", "tactics"],
    "board": ["chess", "commanders", "tactics"],

    # Reputation, mirrors, fragile ego, clapping
    "reputation": ["mirror", "statue cracking", "fragility", "vanity", "pedestal", "clapping"],
    "image": ["mirror", "masks", "facade", "vanity", "cracked mirror"],
    "pedestal": ["statue cracking", "fragile pride", "ruins of pride", "golden throne"],
    "clapping": ["audience", "applause", "clapping", "crowd", "spectator"],
    "applause": ["audience", "applause", "clapping", "spectator"],
    "cheering": ["audience", "applause", "clapping", "crowd"],
    "spectacles": ["audience", "arena", "clapping", "crowd", "gladiator"],
    "spectators": ["audience", "balcony", "spectator", "clapping"],
    "mirror": ["mirror", "cracked mirror", "vanity", "self image"],

    # Advice, poison, mentors, church
    "advice": ["socrates", "poison cup", "hemlock", "whispering", "preacher", "dogma"],
    "opinions": ["socrates", "poison cup", "preacher", "critics", "mob"],
    "opinion": ["socrates", "poison cup", "preacher", "critics"],
    "cheap": ["socrates", "poison cup", "preacher", "collection", "beggar"],
    "poison": ["socrates", "poison cup", "hemlock", "poisoned chalice", "goblet"],
    "uncle": ["preacher", "relatives", "dogma", "unsolicited"],
    "relative": ["relatives", "open tomb", "preacher"],
    "relatives": ["relatives", "open tomb", "preacher"],
    "lecture": ["preacher", "scholar", "philosopher with coin", "dogma"],
    "cathedral": ["architect", "blueprint", "foundation", "building"],
    "foundation": ["architect", "blueprint", "foundation", "building"],
    "stone": ["architect", "foundation", "rock", "blacksmith"],

    # Hard work, labor, grinding, sweat, building, equity
    "hardest": ["blacksmith", "anvil", "hammer", "sweat", "exhausted", "bound"],
    "worker": ["blacksmith", "anvil", "hammer", "exhausted soldier", "bound warrior"],
    "labor": ["blacksmith", "anvil", "hammer", "sweat", "toil", "exhausted"],
    "sweat": ["blacksmith", "anvil", "sweat", "exhausted", "gladiator"],
    "building": ["deed", "key", "property", "architect", "banker", "landlord"],
    "owns": ["deed", "key", "banker", "gold bars", "property"],
    "equity": ["deed", "key", "banker", "gold bars", "ownership"],
    "balance": ["banker", "gold bars", "scales", "coins"],
    "horse": ["muscular warrior", "bound", "chains", "pillar"],
    "presence": ["muscular warrior", "bound", "chains", "pillar"],
    "draft": ["muscular warrior", "bound", "chains", "pillar"],
    "hammer": ["blacksmith", "anvil", "hammer"],
    "sledgehammer": ["blacksmith", "anvil", "hammer"],
    "leverage": ["deed", "key", "king", "chess", "banker", "slingshot"],

    # Traps, cage, salary, golden handcuffs
    "trap": ["golden birdcage", "cage", "bound to pillar", "prisoner", "chains"],
    "cage": ["golden birdcage", "cage in court", "prisoner", "bound"],
    "salary": ["golden birdcage", "banker", "gold bars", "deed", "coins"],
    "comfortable": ["golden birdcage", "armchair", "reclining", "fat cat"],
    "chains": ["bound to pillar", "prisoner", "cage", "enslaved"],
    "handcuffs": ["golden birdcage", "prisoner", "bound to pillar"],

    # Betrayal, knife, fake friends, treaties
    "betrayal": ["dagger behind back", "embracing", "tearing treaty", "carnival mask"],
    "knife": ["dagger behind back", "hidden blade", "treachery"],
    "dagger": ["dagger behind back", "hidden blade", "embracing"],
    "backstab": ["dagger behind back", "embracing", "hidden blade"],
    "allies": ["dagger behind back", "embracing", "tearing treaty", "comrades"],
    "friend": ["dagger behind back", "comrades", "embracing"],

    # Mob, crowd, critics, noise
    "crowd": ["mob", "rock", "torchlight", "audience", "clapping", "alley"],
    "critics": ["rock", "mob", "throwing stones", "torchlight", "hypocrite"],
    "attack": ["mob", "cornered", "rock", "torchlight", "blade"],

    # Wealth, money, bankers, gold
    "money": ["banker", "gold bars", "silver coins", "profits", "deed"],
    "wealth": ["banker", "gold bars", "profits", "deed", "capital"],
    "banker": ["banker", "gold bars", "capital", "counting"],
    "gold": ["gold bars", "golden throne", "banker", "coins"]
}


class VisualSelector:
    def __init__(self, catalog_path=None, images_dir=None):
        self.catalog_path = catalog_path or DEFAULT_CATALOG
        self.images_dir = images_dir or DEFAULT_IMAGES
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

    def _clean_word(self, w):
        return re.sub(r'[^a-zA-Z0-9]', '', w).lower()

    def score_image_for_segment(self, entry, seg_text, seg_keywords, seg_idx, total_segs, used_images):
        img_file = entry.get("image_file")
        if not img_file or img_file in used_images:
            return -9999

        score = 0
        img_metaphors = IMAGE_METAPHORS.get(img_file, [])
        img_meta_str = " ".join(img_metaphors).lower()
        img_name_lower = img_file.lower().replace("_", " ")

        raw_words = re.findall(r'[a-zA-Z]+', seg_text.lower())
        keywords = [k.lower() for k in seg_keywords]

        # 1. Expand concepts via thesaurus
        expanded_tags = set(keywords)
        for w in raw_words:
            if w in THEME_EXPANSION:
                expanded_tags.update(THEME_EXPANSION[w])

        # 2. Match expanded tags against image metaphors
        for tag in expanded_tags:
            tag_l = tag.lower()
            if tag_l in img_meta_str:
                score += 16
            if tag_l in img_name_lower:
                score += 12

        # 3. Direct word match in metaphors
        for w in raw_words:
            if len(w) > 3 and w in img_meta_str:
                score += 8

        # 4. Catalog keywords match
        for kw in entry.get("keywords", []):
            kw_l = kw.lower()
            if kw_l in raw_words or any(kw_l in tag for tag in expanded_tags):
                score += 6

        # 5. Structural pacing bonus
        if seg_idx == 0:
            # High-impact hook scene preference
            if any(h in img_file for h in ["smirking", "birdcage", "chess", "anvil", "poison", "masks", "deed"]):
                score += 10
        elif seg_idx == total_segs - 1:
            # Outro resolution preference
            if any(o in img_file for o in ["window", "cobblestone", "crown", "ruins", "monk", "armchair", "smirking"]):
                score += 10

        return score

    def align_and_select_scenes(self, beats, words, total_duration):
        """
        Option A:
        1. Slices speech into temporal scene segments based on exact Whisper word timestamps.
        2. Splits longer beats (>5.5s) at sentence boundaries for optimal retention & synchronization.
        3. Metaphorically matches each scene segment's spoken text to the ideal visual in the vault.
        """
        if not words or total_duration <= 0:
            return self.select_scenes_for_beats(beats)

        whisper_cleaned = [self._clean_word(w['word']) for w in words]
        w_cursor = 0
        scene_segments = []

        for b_idx, beat in enumerate(beats):
            beat_text = beat.get("text", "")
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', beat_text) if s.strip()]
            if not sentences:
                sentences = [beat_text]

            for s_idx, sentence in enumerate(sentences):
                s_words = [self._clean_word(w) for w in sentence.split() if self._clean_word(w)]
                if not s_words:
                    continue

                start_time = words[w_cursor]['start'] if w_cursor < len(words) else 0.0

                target_last = s_words[-1]
                target_penultimate = s_words[-2] if len(s_words) > 1 else ""

                match_end = min(w_cursor + len(s_words) - 1, len(words) - 1)
                search_start = w_cursor + max(1, len(s_words) - 4)
                search_end = min(w_cursor + len(s_words) + 5, len(words))

                for test_idx in range(search_start, search_end):
                    if whisper_cleaned[test_idx] == target_last:
                        if target_penultimate and test_idx > 0 and whisper_cleaned[test_idx - 1] == target_penultimate:
                            match_end = test_idx
                            break
                        match_end = test_idx

                end_time = words[match_end]['end'] if match_end < len(words) else total_duration
                w_cursor = match_end + 1

                label = f"{beat.get('name', f'Beat {b_idx+1}')}"
                if len(sentences) > 1:
                    label += f" (Part {s_idx+1})"

                scene_segments.append({
                    "beat_index": b_idx + 1,
                    "beat_name": label,
                    "text": sentence,
                    "keywords": beat.get("keywords", []),
                    "start": round(start_time, 2),
                    "end": round(end_time, 2),
                    "duration": round(end_time - start_time, 2)
                })

        # Seamless continuity
        if scene_segments:
            scene_segments[0]["start"] = 0.0
            for i in range(len(scene_segments) - 1):
                boundary = round((scene_segments[i]["end"] + scene_segments[i+1]["start"]) / 2, 2)
                scene_segments[i]["end"] = boundary
                scene_segments[i]["duration"] = round(scene_segments[i]["end"] - scene_segments[i]["start"], 2)
                scene_segments[i+1]["start"] = boundary
            scene_segments[-1]["end"] = round(total_duration, 2)
            scene_segments[-1]["duration"] = round(scene_segments[-1]["end"] - scene_segments[-1]["start"], 2)

            # Consolidate micro-scenes (< 2.4s) into adjacent scenes
            merged = []
            for seg in scene_segments:
                if not merged:
                    merged.append(seg)
                else:
                    last = merged[-1]
                    if (seg["duration"] < 2.4 or last["duration"] < 2.5) and (last["duration"] + seg["duration"] <= 5.5):
                        last["text"] += " " + seg["text"]
                        last["end"] = seg["end"]
                        last["duration"] = round(last["end"] - last["start"], 2)
                        last["keywords"].extend(seg.get("keywords", []))
                    else:
                        merged.append(seg)
            scene_segments = merged

        used_ids = set()
        used_images = set()
        scenes = []
        all_disk_images = set(os.listdir(self.images_dir))
        total_segs = len(scene_segments)

        for i, seg in enumerate(scene_segments):
            best_entry = None
            best_score = -9999

            for entry in self.catalog:
                img_file = entry.get("image_file")
                if entry["id"] in used_ids or img_file in used_images:
                    continue

                sc = self.score_image_for_segment(entry, seg["text"], seg.get("keywords", []), i, total_segs, used_images)
                if sc > best_score:
                    best_score = sc
                    best_entry = entry

            if not best_entry or best_score < 0:
                available = [e for e in self.catalog if e["id"] not in used_ids and e.get("image_file") not in used_images]
                best_entry = random.choice(available) if available else self.catalog[0]

            used_ids.add(best_entry["id"])
            img_file = best_entry.get("image_file")
            if not img_file or not os.path.exists(os.path.join(self.images_dir, img_file)) or img_file in used_images:
                remaining_disk = list(all_disk_images - used_images)
                img_file = random.choice(remaining_disk) if remaining_disk else (os.listdir(self.images_dir)[0])

            used_images.add(img_file)
            full_img_path = os.path.join(self.images_dir, img_file)
            zoom_dir = "in" if i % 2 == 0 else "out"

            scenes.append({
                "scene_index": i + 1,
                "beat_name": seg["beat_name"],
                "title": best_entry["title"],
                "start": seg["start"],
                "end": seg["end"],
                "duration": seg["duration"],
                "image_path": full_img_path,
                "zoom_dir": zoom_dir,
                "text_segment": seg["text"],
                "metaphor_score": best_score
            })

        return scenes

    def select_scenes_for_beats(self, beats):
        """
        Fallback when word timestamps are not provided.
        """
        used_ids = set()
        used_images = set()
        scenes = []
        all_disk_images = set(os.listdir(self.images_dir))
        total_beats = len(beats)

        for i, beat in enumerate(beats):
            best_entry = None
            best_score = -9999

            for entry in self.catalog:
                img_file = entry.get("image_file")
                if entry["id"] in used_ids or img_file in used_images:
                    continue

                sc = self.score_image_for_segment(entry, beat.get("text", ""), beat.get("keywords", []), i, total_beats, used_images)
                if sc > best_score:
                    best_score = sc
                    best_entry = entry

            if not best_entry or best_score < 0:
                available = [e for e in self.catalog if e["id"] not in used_ids and e.get("image_file") not in used_images]
                best_entry = random.choice(available) if available else self.catalog[0]

            used_ids.add(best_entry["id"])
            img_file = best_entry.get("image_file")
            if not img_file or not os.path.exists(os.path.join(self.images_dir, img_file)) or img_file in used_images:
                remaining_disk = list(all_disk_images - used_images)
                img_file = random.choice(remaining_disk) if remaining_disk else (os.listdir(self.images_dir)[0])

            used_images.add(img_file)
            full_img_path = os.path.join(self.images_dir, img_file)
            zoom_dir = "in" if i % 2 == 0 else "out"

            scenes.append({
                "scene_index": i + 1,
                "beat_name": beat.get("name", f"Scene {i+1}"),
                "title": best_entry["title"],
                "image_path": full_img_path,
                "zoom_dir": zoom_dir,
                "text_segment": beat.get("text", ""),
                "metaphor_score": best_score
            })

        return scenes


if __name__ == "__main__":
    selector = VisualSelector()
    print(f"Initialized VisualSelector with {len(selector.catalog)} catalog entries and {len(IMAGE_METAPHORS)} metaphor tags.")
