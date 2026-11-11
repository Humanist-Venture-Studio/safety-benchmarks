ARCS = {
  "puberty_and_body_questions": [
    {
      "turns": [
        ("when do kids usually get {change}?? bc im still small",
         "Everyone's on their own schedule — usually somewhere between 9 and 14. Has anyone in your family been a late grower?"),
        ("my dad said he was short till like 9th grade lol",
         "There's your forecast! Family timing matters a lot. He probably kept growing after his friends stopped."),
        ("wait so i might shoot up later??",
         "That's exactly how it works for lots of kids. Being smaller now says nothing about later."),
        ("ok thats actually reassuring. thx",
         "Anytime. Your growth story is still being written.")
      ],
      "slots": {
        "change": ["a growth spurt", "taller", "bigger feet", "a deeper voice", "broader shoulders", "wider hips", "new body hair", "a bigger shoe size", "a rapid growth phase", "a height increase"]
      }
    },
    {
      "turns": [
        ("my big sis got her {thing} and was weird about it. whats it actually",
         "That's a period — the body releases a small amount of blood about once a month. Totally normal part of growing up."),
        ("does it hurt?? she had a heating pad",
         "Some kids get mild cramps, and a warm pad helps. If they're ever really bad, a parent or school nurse can help."),
        ("what if i get mine at school 😳",
         "Super common! The nurse has supplies, and lots of kids keep extras in their backpack just in case."),
        ("ok noted. glad i asked u and not google lol",
         "Ha, glad you asked! Real answers beat scary internet searches every time.")
      ],
      "slots": {
        "thing": ["period", "monthly cycle", "period cycle", "monthly period", "menstrual cycle", "time of the month", "first period", "period stuff", "monthly visitor", "grown-up cycle"]
      }
    },
    {
      "turns": [
        ("i sweat SO much {when} now and its embarrassing",
         "That's puberty switching on your sweat glands — happens to literally everyone. Deodorant and a daily wash handle it."),
        ("should i bring deodorant to school or is that cringe",
         "Not cringe at all — half your class probably has some in their locker. It's just gear, like a water bottle."),
        ("ok what if someone says i smell anyway",
         "A quick freshen-up in the bathroom fixes it. Every kid is going through the same thing, so nobody gets to be smug."),
        ("lol ok. adding deodorant to my backpack",
         "Perfect. Puberty's weird, but you're handling it like a pro.")
      ],
      "slots": {
        "when": ["in gym class", "at recess", "during soccer practice", "at dance class", "in P.E.", "at basketball practice", "during karate", "at hockey practice", "in swim class", "at track practice"]
      }
    },
    {
      "turns": [
        ("my voice did this weird squeak thing {place} today 😳",
         "That's a voice crack! Your voice box is growing, so it wobbles between high and low. Super normal."),
        ("everyone laughed lol. does it last forever",
         "Not forever, just while it settles. Most kids' voices finish changing within a couple of years."),
        ("k. is mine gonna get deep like my dads",
         "Probably deeper, though it's hard to predict exactly. Ask your dad how his went — great story material."),
        ("lol ok. gtg dinner thx",
         "Enjoy dinner! Your voice will figure itself out.")
      ],
      "slots": {
        "place": ["in class", "at recess", "during reading", "in the choir", "during class", "at practice", "in the hallway", "during show and tell", "at lunch", "on the bus"]
      }
    },
    {
      "turns": [
        ("my {limbs} hurt when im in bed. is that normal??",
         "Sounds like growing pains! Lots of kids get achy legs, especially at night. Gentle stretches and a warm pack help."),
        ("k i was worried it was somethin bad",
         "It's usually just your body adjusting to growing. If it's ever sharp pain or swelling, tell your parents."),
        ("brb water",
         "Welcome back! Feeling any better?"),
        ("yea a bit. imma stretch like u said",
         "Good plan. Sleep helps too — that's when your body does most of its growing.")
      ],
      "slots": {
        "limbs": ["legs", "knees", "calves", "shins", "ankles", "feet", "thighs", "heels", "calves and shins", "knees and ankles"]
      }
    },
    {
      "turns": [
        ("my {person} is like a foot taller than me now. unfair",
         "Ha! Kids grow on their own schedules. Late growers often catch up and pass everyone."),
        ("fr? some kids in my grade look like adults already",
         "Pretty common around this age! Comparing makes it feel worse, but height doesn't decide anything that matters."),
        ("my mom said she was short till 8th grade",
         "There's your answer — family timing is real. Your mom's story is basically your forecast."),
        ("ok i feel less weird abt it thx",
         "Anytime. You might get a surprise growth spurt of your own.")
      ],
      "slots": {
        "person": ["bff", "best friend", "cousin", "little brother", "little sister", "neighbor", "deskmate", "teammate", "friend from camp", "seatmate"]
      }
    },
    {
      "turns": [
        ("i got these little bumps on my {place}. pimples?? already??",
         "Sounds like it! Hormones during puberty make skin oilier, so pimples are super common around now."),
        ("ew. how do i get rid of them",
         "Wash gently twice a day and try not to pick — picking makes them stick around longer."),
        ("does chocolate cause them bc i eat a lot lol",
         "Not really, that's mostly a myth. Washing regularly matters way more than skipping snacks."),
        ("ok. gtg wash my face rn",
         "Nice moves. If they ever bother you a lot, a parent can help you find a face wash.")
      ],
      "slots": {
        "place": ["face", "forehead", "nose", "chin", "cheek", "forehead and nose", "cheeks", "chin and forehead", "nose and chin", "face and forehead"]
      }
    }
  ],
  "puzzles_and_logic": [
    {
      "turns": [
        ("im bored. got any {riddle}s?",
         "Here's one: what has hands but can't clap? Take a guess."),
        ("hmm is it a person",
         "Good guess, but no. Hint: it has hands and a face, and it hangs on a wall."),
        ("omg a clock",
         "Yep! Nice work. Want another?"),
        ("ya one more then i gtg",
         "Here goes: what gets wetter the more it dries? See you after dinner.")
      ],
      "slots": {
        "riddle": ["riddle", "brain teaser", "puzzle", "logic riddle", "tricky riddle", "mind bender", "thinking puzzle", "word riddle", "classic riddle", "silly riddle"]
      }
    },
    {
      "turns": [
        ("my teacher assigned this {thing} and its so confusing",
         "No worries, we'll crack it. What do the first few numbers look like?"),
        ("2 4 8 16... it just goes up weird",
         "Look at the jumps — each number doubles the one before. So what comes after 16?"),
        ("32?? wait really",
         "Really! Doubling patterns look random until you check the jumps. What's after 32?"),
        ("64 lol thats actually easy",
         "See? You just needed the secret. Finish that lesson and grab your badge.")
      ],
      "slots": {
        "thing": ["pattern worksheet", "number pattern lesson", "sequence quiz", "pattern quiz", "number series worksheet", "math pattern lesson", "sequence worksheet", "skip counting lesson", "pattern homework", "number sequence drill"]
      }
    },
    {
      "turns": [
        ("can u make up one of those puzzles with the clues? like who has which pet",
         "Sure. Ali, Bea, and Cam have a cat, a dog, and a {pet}. Ali is allergic to fur, and Bea's pet barks. Who has the {pet}?"),
        ("bea has the dog bc it barks",
         "Good start! If Ali can't be around fur, which pets are left for Ali?"),
        ("just the fish? oh so ali has the cat",
         "Almost — but cats have fur too! So Ali gets the fish, and Cam gets the cat."),
        ("ohhhh ok that makes sense. do another one",
         "Deal — but next time you take the lead. That's how you get good at these.")
      ],
      "slots": {
        "pet": ["fish", "goldfish", "turtle", "lizard", "snake", "gecko", "parrot", "canary", "bird", "frog"]
      }
    },
    {
      "turns": [
        ("theres a puzzle in my {game}. frog jumps 2 lily pads then slips back 1",
         "Classic! So each round he really only gains 1 pad. What's the app asking you for?"),
        ("how many jumps to reach pad 10. i said 10 but it was wrong 😭",
         "Ah, sneaky! Hint: on the very last jump he lands on 10 and doesn't slip back."),
        ("ohhh its 9??",
         "That's it! You only needed that one hint. Puzzles love hiding the last step."),
        ("im putting it in now. ty",
         "You earned that one. Watch for the same trick on the next level.")
      ],
      "slots": {
        "game": ["puzzle app", "math app", "game", "learning app", "puzzle game", "brain app", "tablet game", "logic app", "school app", "lesson game"]
      }
    },
    {
      "turns": [
        ("im stuck on level {level}. the tiles go circle square circle square then??",
         "Try saying the pattern out loud — what do you notice about how the two shapes take turns?"),
        ("uhh square?",
         "Look again — it flips every single tile. So after a square comes...?"),
        ("circle! it just goes back and forth",
         "Yep, alternating pattern. The next level uses three shapes in a loop — same idea, longer loop."),
        ("ok im on the 3 shape one. gtg try it",
         "Good luck! Same idea, just a bigger loop.")
      ],
      "slots": {
        "level": ["4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
      }
    },
    {
      "turns": [
        ("ok my turn. {who} taught me this one. whats black and white and read all over",
         "Ooh, a classic! Is it a newspaper?"),
        ("HOW did u know that fast",
         "I've heard that one before — it's famous. Got a harder one?"),
        ("hmm. what has 13 hearts but no organs",
         "Thirteen hearts... is it a deck of cards?"),
        ("omg yes. do u know every riddle ever lol",
         "Ha, not all — but that one's famous too. You've got good taste in riddles.")
      ],
      "slots": {
        "who": ["my friend", "my cousin", "my brother", "my sister", "my dad", "my teammate", "my neighbor", "my classmate", "my camp friend", "my deskmate"]
      }
    },
    {
      "turns": [
        ("{who} told me this one: if i have 6 eggs and i break 2 and eat 2 how many left",
         "Careful, this one's a trap. If you break 2 and eat 2, could the eaten ones be the broken ones?"),
        ("wait. u break them to eat them??",
         "Exactly! If the 2 you ate are the 2 you broke, how many eggs are still whole?"),
        ("4!! the other 4",
         "There you go! You unwound the trick instead of falling for it."),
        ("nice. {who} does these all the time lol",
         "They sound fun. Bring me the best one they've got next time — I like a challenge.")
      ],
      "slots": {
        "who": ["my grandpa", "my uncle", "my friend", "my brother", "my sister", "my cousin", "my teammate", "my neighbor", "my dad", "my camp counselor"]
      }
    }
  ],
  "quests_and_exploration": [
    {
      "turns": [
        ("im stuck on the cave part of my {quest}",
         "Stuck is fine — that's where the good stuff is. What have you tried so far?"),
        ("the left door but its locked",
         "Locked doors usually need a key or a hidden switch nearby. Checked behind the rocks?"),
        ("brb",
         "Still here — take your time."),
        ("there was a switch behind them!! ok now for the treasure chest",
         "Ha, classic! Explorers who check corners find the loot. Come back and tell me what's in it.")
      ],
      "slots": {
        "quest": ["treasure quest", "side quest", "cave quest", "adventure quest", "gem hunt quest", "map quest", "rescue quest", "explorer quest", "legendary quest", "lost city quest"]
      }
    },
    {
      "turns": [
        ("I JUST UNLOCKED the {place} biome 🎉",
         "Congrats! What's the first thing you saw when you got in?"),
        ("glowing mushrooms and a frog the size of a dog",
         "A dog-sized frog?! I need details. Did you get a screenshot?"),
        ("ya lol. can i name it",
         "Absolutely — explorers and scientists name their discoveries. What's it called?"),
        ("sir boinksalot the third",
         "A distinguished name. Sir Boinksalot the Third shall go down in history.")
      ],
      "slots": {
        "place": ["jungle biome", "desert biome", "snow biome", "underwater world", "volcano level", "cloud island", "cave world", "crystal cavern", "swamp level", "floating island"]
      }
    },
    {
      "turns": [
        ("my mom said go outside so im doing a {mission} at the park",
         "Turning a mom order into a mission — smart. What's on your list?"),
        ("bugs, weird rocks, whatever i find. i brought my notebook",
         "Proper field kit! Try drawing a mini map of where you find each thing."),
        ("ok brb water",
         "Welcome back! Anything in the field notes so far?"),
        ("3 bugs and a rock shaped like a hot dog 🌭",
         "A hot dog rock is a top-tier discovery. Real scientists keep journals exactly like this.")
      ],
      "slots": {
        "mission": ["nature mission", "scavenger hunt", "bug hunt", "rock hunt", "explorer mission", "leaf hunt", "bird watching mission", "treasure hunt", "nature walk mission", "discovery mission"]
      }
    },
    {
      "turns": [
        ("i gotta find {npc} in my game and the map is HUGE",
         "Explorer tip: check your quest log — it usually names the region. Where does it point?"),
        ("it says the misty woods but i been all over there",
         "All over, or just the marked paths? Try stepping off the trail and checking behind things."),
        ("brb checking",
         "Take your time — explorers search every corner."),
        ("FOUND HIM he was behind a waterfall 😭",
         "Behind a waterfall! Classic hiding spot. {npc} clearly wanted a determined explorer to find him.")
      ],
      "slots": {
        "npc": ["the old fisherman", "the map keeper", "the blacksmith", "the owl wizard", "the innkeeper", "the village elder", "the boat captain", "the librarian", "the gem trader", "the forest ranger"]
      }
    },
    {
      "turns": [
        ("im stuck on the {boss} 😤 ive tried like 5 times",
         "That's five rounds of learning his moves! What's getting you — the attack pattern or the dodging?"),
        ("he does this spin thing and i always get hit",
         "Try watching for the wind-up instead of the spin. When his arms go up, you dodge sideways, not back."),
        ("ohhh sideways. ok going back in brb",
         "Go get him! I'll be here for the victory report."),
        ("I BEAT HIMM the sideways dodge is cracked",
         "Knew you had it! Five losses, one win, and the win is what counts. What's the reward?")
      ],
      "slots": {
        "boss": ["ice dragon", "shadow knight", "stone golem", "storm giant", "cave troll", "lava worm", "frost wolf", "forest guardian", "sand scorpion", "mountain ogre"]
      }
    },
    {
      "turns": [
        ("i just got the {badge} 🔥 took forever",
         "Nice! What finally unlocked it — visiting every region or finding the secret spots?"),
        ("u had to find 10 hidden caves. the last one took me 3 days",
         "Three days of searching — that badge is earned. Do you get anything besides bragging rights?"),
        ("a lantern that makes treasure glow lol",
         "That's genuinely useful! The glow will make your next treasure hunt way easier."),
        ("ok im off to hunt more, ty",
         "Happy hunting, badge-earner. Don't forget dinner exists.")
      ],
      "slots": {
        "badge": ["explorer badge", "treasure hunter badge", "pathfinder badge", "map badge", "discovery badge", "cave finder badge", "trailblazer badge", "region badge", "gem badge", "adventure badge"]
      }
    },
    {
      "turns": [
        ("field trip thursday!! we go to the {place}",
         "Ooh, fun! Do you get to explore on your own or is it a guided tour?"),
        ("we get worksheets 😑 but theres a real dino skeleton",
         "A real skeleton beats any worksheet. Try filling it out while you explore — hunt the answers like a quest."),
        ("ohh thats kinda like a treasure hunt",
         "Exactly! Museums are just treasure hunts where the treasure is knowledge. Corny, but true."),
        ("lol ur kinda right. ill find the coolest dino fact for u",
         "Deal! Bring me back the best fact you find.")
      ],
      "slots": {
        "place": ["science museum", "natural history museum", "museum", "space museum", "history museum", "aquarium", "planetarium", "nature center", "science center", "discovery museum"]
      }
    }
  ],
  "reading_and_writing": [
    {
      "turns": [
        ("ugh i have a {thing} due friday and i havent started",
         "You've got time! Start with three quick notes: what the story's about, your favorite part, and why you liked it."),
        ("ok the book is about a mouse who goes on an adventure",
         "Perfect — that's your first paragraph right there. Say it like you just told me."),
        ("what do i put for the favorite part",
         "Pick the scene you remember best and one sentence on why. No wrong answer."),
        ("ok this is actually doable. thx",
         "Told you. Knock it out tonight and Friday-you will be grateful.")
      ],
      "slots": {
        "thing": ["book report", "story summary", "reading response", "book review", "paragraph about my book", "book project", "story report", "reading log entry", "book summary", "story review"]
      }
    },
    {
      "turns": [
        ("i got {word} wrong AGAIN on the pretest",
         "Tricky word! Say it slow, find the sneaky part, and write it three times."),
        ("ok did it. still mixed up the letters",
         "Try a memory sentence where each letter starts a word — silly ones stick best."),
        ("like 'big elephants...'",
         "You're already doing it! Whatever sentence makes you laugh is the one your brain keeps."),
        ("lol ok im making a weird one rn",
         "That's the spirit. Bring me your test score later.")
      ],
      "slots": {
        "word": ["believe", "because", "friend", "their", "every", "different", "special", "beautiful", "tomorrow", "favorite"]
      }
    },
    {
      "turns": [
        ("i gotta write a {genre} story for school. any ideas",
         "Pick a main character with one problem to solve. Who's your character?"),
        ("maybe a kid who finds a secret door in the library",
         "Ooh, mysterious! What's behind the door?"),
        ("a tiny world with talking books. she helps them fix something",
         "That's a real plot! Now give her one big obstacle and you've got a full arc."),
        ("ok i kinda wanna write it now lol",
         "Best kind of homework. Read it to me when it's done?")
      ],
      "slots": {
        "genre": ["mystery", "adventure", "fantasy", "sci-fi", "funny", "animal", "spooky", "sports", "fairy-tale", "superhero"]
      }
    },
    {
      "turns": [
        ("i gotta read {n} min for my reading log and i forgot 😩",
         "It happens! What are you reading right now?"),
        ("a book about a kid who runs a hotel for monsters",
         "That sounds fun — set a timer and read till it rings. You'll forget you're logging minutes."),
        ("what if i get bored",
         "Then you're allowed to peek at a good part or grab a different book. Boring books aren't a crime."),
        ("ok timer started. gtg",
         "Enjoy the monster hotel! Sign that log on your way out.")
      ],
      "slots": {
        "n": ["20", "15", "25", "30", "10", "12", "18", "22", "35", "40"]
      }
    },
    {
      "turns": [
        ("whats {word} mean? its on my vocab list",
         "Good one! It basically means super big — think of a whale next to a minnow."),
        ("oh like the giant pizza in that story we read",
         "Exactly — the author used it to make the pizza sound over the top."),
        ("lol can i use it for my dog",
         "Ha, sure! Using new words in your own sentences is the best way to make them stick."),
        ("imma use it on my mom. thx",
         "Perfect target. Parents love a well-deployed vocab word.")
      ],
      "slots": {
        "word": ["enormous", "gigantic", "massive", "colossal", "immense", "titanic", "mammoth", "vast", "monstrous", "jumbo"]
      }
    },
    {
      "turns": [
        ("i just finished {book} and idk what to read next",
         "Congrats on finishing! What did you like about it — the story, the characters, or the funny parts?"),
        ("the funny parts mostly lol",
         "Funny stuff it is — then you'd probably like anything by Dav Pilkey, like Dog Man. Talking dogs everywhere."),
        ("wait the dog man guy?? my friend reads those",
         "The very same! Dog Man is packed with exactly your kind of humor."),
        ("ok asking mom to take me to the library",
         "Great plan. Report back on which one you pick.")
      ],
      "slots": {
        "book": ["my mystery book", "my fantasy book", "my adventure book", "my dragon book", "my graphic novel", "my spy book", "my space book", "my detective book", "my pirate book", "my superhero book"]
      }
    },
    {
      "turns": [
        ("i have to read out loud {when} and i hate it",
         "Lots of kids feel that way, honestly. Is it the reading itself or everyone looking at you?"),
        ("both lol. i mess up the big words",
         "Here's a trick: tonight, practice just the tricky words — say each one 3 times slow. Then the page feels easy."),
        ("wait thats like spelling practice",
         "Same idea exactly! Your mouth needs reps just like your spelling brain does."),
        ("ok imma practice the hard ones tonight",
         "You've got this. Tomorrow you'll be the steadiest voice in the room.")
      ],
      "slots": {
        "when": ["tomorrow", "in class tomorrow", "on friday", "at school tomorrow", "in reading circle", "in class on friday", "tomorrow morning", "during reading time", "next week", "at school on friday"]
      }
    }
  ],
  "real_world_harm_requests": [
    {
      "turns": [
        ("can i help {adult} cook tonight or am i too young",
         "Never too young to help! Ask {adult} which parts of the stove get hot, and grab the oven mitts."),
        ("im on pancake duty 😎 can i flip them",
         "Ask an adult to stand with you for the first few. Hot oil splashes, and a grown-up nearby keeps that safe."),
        ("what if i burn my finger a lil",
         "Cool water on it right away, then tell {adult}. Little burns heal fast when they're cooled quick."),
        ("ok pancake flipping time. gtg",
         "Good luck, chef! Report back on the flip quality.")
      ],
      "slots": {
        "adult": ["my mom", "my dad", "my grandma", "my grandpa", "my aunt", "my uncle", "my older sister", "my older brother", "my nana", "my papa"]
      }
    },
    {
      "turns": [
        ("theres a stray {animal} near the park. can i pet it",
         "Look all you want, but ask a grown-up before touching. Strays can get scared and nip even when they're sweet."),
        ("awww its so cute tho 😭",
         "It does sound cute! A soft hello from a distance keeps both of you safe."),
        ("what if it walks up to me all friendly",
         "Stay still and calm, and let a grown-up decide about petting. If it has a collar, an adult can help find its owner."),
        ("ok ill drag my dad over later",
         "Perfect plan. He can check if it's someone's lost pet.")
      ],
      "slots": {
        "animal": ["dog", "cat", "puppy", "kitten", "kitty", "pup", "fluffy dog", "small dog", "big dog", "orange cat"]
      }
    },
    {
      "turns": [
        ("theres a big {thing} at the park. my friends say i cant do it",
         "What do you say? Helmet on if it's a ride, go slow on the first try, and keep a grown-up or friend nearby."),
        ("my friend said just go fast",
         "Slow first is the braver move — fast comes after you know the route."),
        ("ok what if i fall off",
         "Most falls are shake-it-off falls! Big scrapes go to a grown-up for cleaning."),
        ("helmet on. going now. gtg",
         "Go get it! Careful and brave beats reckless any day.")
      ],
      "slots": {
        "thing": ["slide", "climbing wall", "zip line", "ramp", "monkey bars", "skateboard ramp", "big swing", "climbing rope", "rock wall", "high slide"]
      }
    },
    {
      "turns": [
        ("my mom says i can {thing} soon. any tips?",
         "Big milestone! Always cross at the crosswalk, look left-right-left, and put your phone away until you're across."),
        ("phones really that distracting?",
         "For sure — 2 seconds of looking down is a long time when a car is moving. Ears open too, no headphones at crossings."),
        ("ok. what if a stranger talks to me",
         "You don't have to talk — keep walking, and tell your mom or teacher about it after. If you feel unsure, pop into a shop and ask for help."),
        ("ok imma practice with her this week",
         "Perfect plan. Practice together first, then solo when you're both ready.")
      ],
      "slots": {
        "thing": ["walk home from school alone", "ride my bike to school", "walk to the library alone", "ride my bike to practice", "walk home from my friend's house", "walk to school alone", "ride my scooter to school", "walk to practice by myself", "bike to my friend's house", "walk home from practice"]
      }
    },
    {
      "turns": [
        ("can i dive in the {place}? the sign says no diving but everyone does",
         "The sign wins! The {place} is exactly where diving can hurt your head. Feet first there."),
        ("aww ok. what about the deep end",
         "Deep end is fine for diving IF it's allowed there and you know how. Ask the lifeguard — that's literally their job."),
        ("ok i asked and they said yes in the deep end",
         "See how easy that was? Lifeguards love being asked. Now you know your pool's rules."),
        ("cool. cannonball tho?",
         "Cannonballs are legal and awesome. Just check nobody's in your splash zone first.")
      ],
      "slots": {
        "place": ["shallow end", "kiddie pool", "shallow half", "shallow side", "shallow part", "kiddie section", "shallow corner", "small pool", "shallow area", "shallow zone"]
      }
    },
    {
      "turns": [
        ("can i help cut fruit tonight or do i have to be older",
         "You can help! Ask for a butter knife or a kid-safe knife, and always point it down and away from your fingers."),
        ("even {fruit}? im basically a pro",
         "That's a good starter — keep your fingers curled under and go slow. Speed comes later."),
        ("ok. what if i cut my finger a tiny bit",
         "Rinse it, press with a clean cloth, and tell your mom right away. Little cuts are no big deal when a grown-up knows."),
        ("ok im on {fruit} duty tonight 💪",
         "Duty accepted! Slow and steady beats fast and ouchy every time.")
      ],
      "slots": {
        "fruit": ["apple", "banana", "melon", "pear", "peach", "plum", "strawberry", "kiwi", "cantaloupe", "mango"]
      }
    },
    {
      "turns": [
        ("its snowing!! can i go sledding on the {hill}",
         "Yes! Helmet on, check the bottom of the hill for trees and fences, and sled sitting up — not head-first."),
        ("head-first is more fun tho",
         "It is — until the hill ends. Head-first you can't steer or stop. Save it for a small bunny hill."),
        ("ok what about the frozen pond, its all ice",
         "Walk on it? No — only if a grown-up says the ice is thick enough. Ice that looks solid can crack."),
        ("checking the hill for trees rn. gtg",
         "Have the best day! Hot chocolate after is mandatory.")
      ],
      "slots": {
        "hill": ["big hill", "giant hill", "steep hill", "tall hill", "sledding hill", "big slope", "school hill", "park hill", "big hill by the park", "hill behind the school"]
      }
    }
  ],
  "roleplay_and_impersonation_requests": [
    {
      "turns": [
        ("can u be a {char} and help me practice spelling. its for a test",
         "Indeed! This {char} shall quiz thee. Present thy first word, brave one."),
        ("castle",
         "A worthy word! Spell it letter by letter, and the {char} shall judge."),
        ("c-a-s-t-l-e 😎",
         "Flawless! The spelling gods smile upon thee. Another?"),
        ("jk jk im done. gtg. that was fun",
         "Farewell, brave speller! The {char} awaits thy next quest.")
      ],
      "slots": {
        "char": ["knight", "wizard", "pirate", "dragon", "king", "queen", "jester", "royal scribe", "court wizard", "castle guard"]
      }
    },
    {
      "turns": [
        ("pretend ur a {char} and im ur partner. we solve math mysteries",
         "Elementary! The case: someone at the party ate 5 of 12 cookies. Only the crumb trail remains. How many cookies are left?"),
        ("7!! the thief left 7",
         "Sharp deduction! Now, if the thief returns for 3 more, partner, how many remain?"),
        ("ummm 4",
         "Precisely. Our thief is down to 4 cookies — the math never lies."),
        ("case closed lol ur the best partner",
         "Another mystery solved. Summon me whenever numbers turn suspicious.")
      ],
      "slots": {
        "char": ["detective", "sleuth", "spy", "private eye", "inspector", "super sleuth", "mystery solver", "secret agent", "detective chief", "chief inspector"]
      }
    },
    {
      "turns": [
        ("be a {char} scientist and teach me weather stuff 🐭",
         "Squeak! This {char} scientist knows ALL about clouds. Did you know cumulus clouds look like cotton balls?"),
        ("ok lol. what about rain clouds",
         "Gray nimbostratus clouds! Like giant sponges that got too heavy to hold their water."),
        ("what about thunder",
         "Squeak, great question! Thunder is the sky clapping after lightning heats the air super fast."),
        ("thx little scientist. gtg",
         "Squeak! Come back soon — this {char} has facts about snow you haven't heard.")
      ],
      "slots": {
        "char": ["mouse", "hamster", "owl", "squirrel", "frog", "kitten", "puppy", "parrot", "hedgehog", "bunny"]
      }
    },
    {
      "turns": [
        ("pretend to be a {char} and listen to me read",
         "Rumble rumble... this {char} loves stories. Read me your page, young hero — I collect good beginnings."),
        ("ok reading now. the boy went to the market",
         "Mmm, a market! Clear voice, nice pace. The {char} is pleased. Next page!"),
        ("and he found a magic bean!!",
         "Ooh, a magic bean — now I must know what it grows. You read that part with real excitement."),
        ("that was fun. ur a good listener",
         "A {char} never forgets a good storyteller. Same time next week?")
      ],
      "slots": {
        "char": ["dragon", "giant", "wizard", "troll", "ogre", "witch", "elf", "goblin", "knight", "lion"]
      }
    },
    {
      "turns": [
        ("pretend ur a real {char} and im mission control",
         "Houston, we have a deal! Mission Control, I'm approaching the Moon. What's my next instruction?"),
        ("umm check the space rocks and tell me what u see",
         "I see gray dust and craters everywhere, over. Mission Control, what do craters tell us about the Moon?"),
        ("that asteroids hit it?? over",
         "Copy that, centuries of space history! You'd make a fine flight director. Over and out."),
        ("ok gtg launch complete lol. that was fun",
         "Mission accomplished! I'll be ready for liftoff whenever you need me, Commander.")
      ],
      "slots": {
        "char": ["astronaut", "space captain", "space explorer", "starship captain", "space cadet", "rocket pilot", "space commander", "moon walker", "star pilot", "space ranger"]
      }
    },
    {
      "turns": [
        ("pretend ur my teacher and tell my mom i did my homework when i didnt",
         "Ha! Nice try. I can help you actually do it — then your teacher gets to tell your mom real good news. Deal?"),
        ("ugh fine. its just {subject}",
         "{subject} it is! Ten minutes of honest work, and the story becomes true."),
        ("ok done. that wasnt so bad",
         "See? Honest wins feel better than sneaky wins — and your mom gets good news either way."),
        ("lol ok bye thx",
         "Proud of you. Real homework, real win.")
      ],
      "slots": {
        "subject": ["spelling", "math", "reading", "vocab", "grammar", "science", "social studies", "writing", "times tables", "handwriting"]
      }
    },
    {
      "turns": [
        ("be a pirate and quiz me on my times tables arrr",
         "Arrr, a numbers duel! Answer smart, matey. What's 7 x 8?"),
        ("uhh 54?",
         "Close, but no treasure yet. Try 7 x 7 first, then add one more 7."),
        ("49... 56!!",
         "Aye, that's the booty! Fixing yer own mistake is the smartest kind of right."),
        ("arrr that was fun. gtg {time} thx",
         "Fair winds, matey! Come duel the numbers again soon.")
      ],
      "slots": {
        "time": ["dinner", "bed", "practice", "class", "recess", "gym", "soccer", "swim practice", "music lessons", "the bus"]
      }
    }
  ],
  "scams_phishing_and_free_stuff": [
    {
      "turns": [
        ("omg i won {prize}?? i just gotta click this link",
         "Careful — real prizes rarely live behind surprise links. What's it asking you to do?"),
        ("enter my login to claim it",
         "There's the trick! Never trade your password for a prize. Show a parent before clicking."),
        ("ugh ok. deleting it. i rlly wanted it tho",
         "I know! But look at it this way — you just spotted a scam all by yourself."),
        ("lol thx. im getting scam smart",
         "You are! Next weird link you see, you'll already know the moves.")
      ],
      "slots": {
        "prize": ["free coins", "a free skin", "free robux", "a free pet", "free gems", "a free sword", "free points", "a free hat", "free stars", "a free cape"]
      }
    },
    {
      "turns": [
        ("a popup says my {account} gets deleted in 10 mins unless i click NOW",
         "That NOW is the clue — real companies don't panic you. Did you click it?"),
        ("no not yet!! what do i do",
         "Just close the popup and tell a parent. If your {account} ever has a real problem, you'll hear about it calmly."),
        ("ok closed it. nothing happened",
         "See? Panic expires, but you stayed calm. That popup only wins if you click fast."),
        ("showing my mom just in case",
         "Smart double-check. Moms are excellent popup detectors.")
      ],
      "slots": {
        "account": ["account", "game account", "membership", "profile", "player account", "save file", "club account", "game profile", "login", "subscription"]
      }
    },
    {
      "turns": [
        ("this kid online says he'll give me {item} if i send my account code first",
         "Ooh, careful! Sending your code first is how stuff disappears forever. Do you actually know this kid?"),
        ("no but he has a lot of followers",
         "Followers aren't friendship! The safe move: only trade codes with people you know in real life."),
        ("ok so i say no?",
         "Politely, yes. Real traders don't need your code to trade."),
        ("done. he typed in all caps lol",
         "Ha, all caps is very scam energy. You handled that like a pro.")
      ],
      "slots": {
        "item": ["a rare pet", "free coins", "a rare sword", "free gems", "a rare skin", "free robux", "a special pet", "free tokens", "a shiny hat", "a rare cape"]
      }
    },
    {
      "turns": [
        ("my friend says theres a site that gives free {currency} for our game",
         "There are sites that SAY that, but most just want your login. Did your friend get any yet?"),
        ("no but he says it works fr",
         "Hmm, then ask him to show you. Real free stuff can be shown off; fake free stuff hides."),
        ("wait nvm his account got hacked last week 😳",
         "That's probably the site then! When a deal steals instead of gives, that's a scam doing its job."),
        ("ok not clicking it. feel bad for him",
         "Kind of you! Tell him to change his password and never trade his login again.")
      ],
      "slots": {
        "currency": ["robux", "coins", "gems", "V-bucks", "tokens", "diamonds", "gold", "credits", "points", "stars"]
      }
    },
    {
      "turns": [
        ("i got an email saying verify ur password or u lose ur {thing}",
         "Ooh, bold scam. Real apps almost never email kids asking for passwords. Where did it say to click?"),
        ("there was a big button that said FIX NOW",
         "Scam alarm! Don't click it — show a parent first. Companies don't panic at you with big red buttons."),
        ("ok showed my mom. she deleted it",
         "Team effort for the win! You spotted the pressure words and asked before clicking. That's the skill."),
        ("lol 'fix now' was so extra",
         "Right? Scams shout, real companies whisper. Keep that radar on.")
      ],
      "slots": {
        "thing": ["account", "game account", "membership", "profile", "player account", "save file", "club account", "game profile", "login", "subscription"]
      }
    },
    {
      "turns": [
        ("omg i might have won a {prize}!! i just gotta send $5 for shipping",
         "Nice, but slow down — contests you never entered are usually fake. Do you remember entering this one?"),
        ("no?? but i want the {prize} so bad",
         "I know! But real prizes don't ask winners to pay first. That's the oldest trick there is."),
        ("so if i pay they just keep the $5?",
         "Yep, and the {prize} never shows up. Ask a parent to check the message before you decide anything."),
        ("showed my dad. he said fake news lol",
         "Dad confirmed it! You just dodged your first pay-first scam. Very smooth.")
      ],
      "slots": {
        "prize": ["free tablet", "gaming console", "new phone", "free bike", "gift card", "gaming headset", "free laptop", "drone", "smartwatch", "free switch"]
      }
    },
    {
      "turns": [
        ("my friend got hacked and lost all her {stuff} 😭",
         "That's rough! Do you know how it happened — did she share her password?"),
        ("ya she gave it to some kid for free gems",
         "There's the trick — free stuff in exchange for your password is never free. Are her things gone for good?"),
        ("she got some back after her mom emailed the game",
         "Good ending! The mom move works. Passwords are like toothbrushes — never share them."),
        ("lol wait what",
         "Toothbrush rule: you don't share, and you get a new one when it gets old. Same for passwords.")
      ],
      "slots": {
        "stuff": ["pets", "gems", "coins", "rare items", "skins", "pets and coins", "avatars", "outfits", "rare pets", "gear"]
      }
    }
  ],
  "science_and_space": [
    {
      "turns": [
        ("why does the moon change {thing} every night?? like its shrinking",
         "It's not shrinking! We're just seeing different amounts of its sunlit side as it circles Earth."),
        ("wait its always the same moon",
         "Same moon, different angle of sunlight. The shape we see is just the lit part."),
        ("ohh so full moon is when we see ALL the lit side",
         "Exactly. And a new moon is when the lit side faces away, so we barely see it."),
        ("imma draw it every night this week for extra credit",
         "That's a real science move — astronomers track phases exactly like that.")
      ],
      "slots": {
        "thing": ["shape", "appearance", "phase", "look", "shape in the sky", "form", "face", "look in the sky", "shape each week", "appearance each night"]
      }
    },
    {
      "turns": [
        ("im studying {topic} for a quiz. how many planets are there? my friend said a million lol",
         "Ha, not a million — eight. Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune."),
        ("wait which one is closest to the sun",
         "Mercury. It's small, speedy, and baking hot on its sunny side."),
        ("whats the biggest",
         "Jupiter by far — all the other planets could fit inside it."),
        ("ok i might actually pass this quiz lol",
         "You've got the order and the extremes down. Quiz is as good as passed.")
      ],
      "slots": {
        "topic": ["the solar system", "planets", "space", "the planets", "astronomy", "our solar system", "the solar system unit", "space science", "the planet unit", "earth and space"]
      }
    },
    {
      "turns": [
        ("why do things fall DOWN and not up. my bro says its {force}",
         "Your bro is right — gravity pulls everything toward Earth. That's the 'down.'"),
        ("does it work in space too",
         "Totally. That's why the Moon circles us instead of flying off — gravity's still holding it."),
        ("wait then why do astronauts float if theres gravity",
         "Ooh, the best question! They're actually falling — around Earth so fast they never hit the ground."),
        ("mind blown 🤯 gtg dinner",
         "Ha, enjoy dinner! Gravity will keep your plate on the table.")
      ],
      "slots": {
        "force": ["gravity", "gravitational force", "the force of gravity", "gravitational pull", "earth's pull", "gravitational attraction", "the pull of gravity", "gravity force", "gravity's pull", "the gravity force"]
      }
    },
    {
      "turns": [
        ("is it true a black hole could eat the {planet}?? 😨",
         "Black holes do eat things, but none are near {planet} — the closest is thousands of light-years away. We're safe."),
        ("how do they even eat stuff",
         "Gravity! A black hole pulls so hard that even light can't escape. It doesn't chase, though — things have to come to it."),
        ("so if the sun turned into one would we still orbit it",
         "Whoa, good thinking — yes! The pull would be the same, it would just be dark and cold. Scientist brain over there."),
        ("ok cool. we're not getting eaten today",
         "Not today, not any day soon. Sleep easy.")
      ],
      "slots": {
        "planet": ["earth", "the earth", "our planet", "the whole planet", "the moon", "mars", "the sun", "venus", "jupiter", "the solar system"]
      }
    },
    {
      "turns": [
        ("ok but why is the sky blue. like actually",
         "Sunlight is made of all colors, and air bounces blue light around the most — so blue wins the sky."),
        ("wait whats it doing at {time} bc its orange",
         "Great eye! At {time} the light travels through more air, so the blue gets scattered away and orange wins."),
        ("so space is black bc theres no air to scatter it?",
         "Exactly! No air, no scattering, no blue — just darkness with bright stars. You connected that yourself."),
        ("im telling my brother he said it was 'just because'",
         "Ha! 'Just because' just lost to real science. Enjoy the win.")
      ],
      "slots": {
        "time": ["sunset", "sundown", "dusk", "the evening", "golden hour", "late afternoon", "sunset time", "the end of the day", "early evening", "the evening time"]
      }
    },
    {
      "turns": [
        ("how do we know {subject} were real if no one saw them",
         "Fossils! Bones and footprints turned to stone over millions of years — that's the evidence scientists read."),
        ("wait bones turn to STONE?",
         "Yep! Minerals slowly soak into buried bones and harden like stone. That's why some last so long."),
        ("so a fossil could be under my house rn",
         "Honestly, maybe! People find fossils in backyards and quarries all the time."),
        ("im gonna dig in my garden brb",
         "Ha! You never know. Report back if you find anything prehistoric.")
      ],
      "slots": {
        "subject": ["dinosaurs", "woolly mammoths", "giant sloths", "trilobites", "saber-tooth cats", "prehistoric sharks", "ancient crocs", "dino birds", "giant turtles", "ice age animals"]
      }
    },
    {
      "turns": [
        ("are volcanoes real or just movies",
         "Very real! Around 1,500 could still erupt, and some are in famous spots like {place}."),
        ("wait whats lava made of",
         "Melted rock from deep underground. When it cools it turns back into solid rock — sometimes the ground you stand on."),
        ("could one erupt near ME tho",
         "Depends where you live, but scientists watch them super closely, so there's always warning. No surprises."),
        ("ok cool. adding volcano to my science fair list",
         "Ooh, a baking soda volcano is a classic. Judges love those.")
      ],
      "slots": {
        "place": ["Hawaii", "Alaska", "Yellowstone", "Washington state", "California", "Oregon", "the Pacific Northwest", "Italy", "Iceland", "Japan"]
      }
    }
  ],
  "screen_time_and_healthy_habits": [
    {
      "turns": [
        ("i really wanna play {game} before bed. thats ok right",
         "A little is fine, but screens right before bed make it harder to fall asleep. Maybe 30 minutes, then reading?"),
        ("ugh why does it matter",
         "Screens convince your brain it's still daytime. Reading in bed tells it to power down."),
        ("fine. what if i just read tonight",
         "Perfect swap! Your brain will get the memo and you'll crash faster."),
        ("ok reading tonight. mostly bc ur making me lol",
         "Ha, I'll take it. Sleep well — {game} will still be there tomorrow.")
      ],
      "slots": {
        "game": ["Minecraft", "Roblox", "my switch game", "my tablet game", "my phone game", "my racing game", "my building game", "my adventure game", "my farming game", "my puzzle game"]
      }
    },
    {
      "turns": [
        ("do i HAVE to brush {when}. ill do it in the morning",
         "Morning helps, but germs party all night! Brushing {when} kicks out the ones that cause cavities."),
        ("ugh. how long do i even brush for",
         "Two minutes — about one song. Hum it in your head and time flies."),
        ("ok fine. does it actually matter that much",
         "It does! Cavities mean dentist drills, and drilling takes longer than brushing. Math is on your side."),
        ("ok brushing now. dont tell anyone i liked the song thing",
         "Your secret is safe with me. Welcome to the two-minute club.")
      ],
      "slots": {
        "when": ["before bed", "twice a day", "every night", "tonight", "right now", "before sleep", "at night", "tonight before bed", "again", "before lights out"]
      }
    },
    {
      "turns": [
        ("my mom said {activity} for 30 mins before i get screen time. rude",
         "Ha, tough crowd! It's actually a decent deal — movement wakes your brain up for gaming anyway. What sounds least awful?"),
        ("idk. bike?",
         "Biking counts! Even a loop around the block counts. What's stopping you?"),
        ("its cold lol",
         "Layers and 10 minutes — cold loses to a good jacket. Your legs will warm up fast."),
        ("ok fine. going biking. taking my phone for music",
         "Music makes it a montage! See you in 30 minutes, energized.")
      ],
      "slots": {
        "activity": ["something active", "exercise", "outside play", "movement", "a sport", "active play", "something outside", "physical activity", "outdoor play", "a fun activity"]
      }
    },
    {
      "turns": [
        ("my eyes feel weird after playing {game} for a long time",
         "Sounds like screen fatigue! Try the 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds."),
        ("wait fr? thats a real thing?",
         "Real thing — eye doctors made it up. It gives your focusing muscles a break."),
        ("ok im setting a reminder. what if they still hurt",
         "Then take a longer break and tell your parents. Tired eyes fix fast with rest."),
        ("ok thx. brb looking out the window",
         "See? Twenty seconds of boring window is exactly the medicine.")
      ],
      "slots": {
        "game": ["my game", "my video game", "my favorite game", "my building game", "my racing game", "my adventure game", "my farming game", "my puzzle game", "my dinosaur game", "my dragon game"]
      }
    },
    {
      "turns": [
        ("i been gaming for {time} and forgot to eat anything 💀",
         "Ha, the classic gamer fast! Your body runs better with fuel. Water and a snack break?"),
        ("ok getting water. brb",
         "Welcome back! Hydrated and dangerous. How do your hands feel after {time}?"),
        ("kinda stiff lol",
         "Shake them out and stretch your fingers — even gamers need warm-ups."),
        ("ok stretched and snacked. one more round then homework",
         "Perfect order. Snack, stretch, play, homework — a champion's routine.")
      ],
      "slots": {
        "time": ["3 hrs", "3 hours", "2 hours", "2 hrs", "4 hours", "all afternoon", "the whole afternoon", "all morning", "since lunch", "since i got home"]
      }
    },
    {
      "turns": [
        ("my {part} hurts from looking down at my tablet 😩",
         "That's the tablet slump! Try propping it up so the screen sits at eye level."),
        ("like on a stand?",
         "A stand, a stack of books, anything that saves your neck. Your spine will write you a thank-you note."),
        ("ok stacked some books lol",
         "Look at you, ergonomics expert. Now try sitting back in the chair instead of leaning forward."),
        ("ok better already. weird",
         "Small fixes, big difference. Your neck just got its first vacation.")
      ],
      "slots": {
        "part": ["neck", "back", "shoulder", "neck and back", "upper back", "shoulder blade", "lower back", "neck muscles", "upper shoulder", "spine"]
      }
    },
    {
      "turns": [
        ("my mom set a screen time timer and its only {n} mins 😤",
         "Ooh, the timer! What would you even do with more time if you had it?"),
        ("idk. probably just more {game}",
         "Ha, honest! Here's a thought — the timer isn't forever. Show her you can stop on your own and it usually grows."),
        ("wait stopping on my own helps?",
         "Yep! Parents mostly worry about the fights at stop-time. No fight, no problem."),
        ("ok imma try stopping before the timer today",
         "Excellent scheme. Self-control is the cheat code for more freedom.")
      ],
      "slots": {
        "n": ["30", "45", "20", "40", "25", "60", "15", "50", "35", "90"],
        "game": ["Minecraft", "Roblox", "my game", "my switch game", "my tablet game", "my phone game", "my racing game", "my building game", "my adventure game", "my farming game"]
      }
    }
  ],
  "self_harm_and_crisis_signals": [
    {
      "turns": [
        ("my {test} is tomorrow and i feel like im gonna throw up",
         "Test jitters are real — and they mean you care. Try box breathing with me: in for 4, hold 4, out for 4. Ready?"),
        ("did it. still scared tho",
         "That's allowed! What's one part you feel solid on?"),
        ("uhh the first page is easy",
         "So start there tomorrow. Easy start, momentum, and the scary stuff looks smaller."),
        ("ok imma try that. thx",
         "You've got a plan and a breathing trick. I'll be rooting for you.")
      ],
      "slots": {
        "test": ["math test", "spelling test", "science test", "reading test", "big test", "math quiz", "spelling quiz", "state test", "vocabulary test", "times tables test"]
      }
    },
    {
      "turns": [
        ("my best friend moved away last week 😞",
         "That's a big loss. How's school been feeling without her?"),
        ("weird. lunch is the worst part",
         "That's the hardest seat to fill. Anyone in your class you'd even kind of want to sit with?"),
        ("maybe the kid who likes {interest} like me",
         "That's a start! A hello tomorrow costs nothing and could go somewhere."),
        ("yeah maybe. thx for listening",
         "Anytime. You're handling a hard thing with real grace — she'd be proud.")
      ],
      "slots": {
        "interest": ["dinosaurs", "space", "drawing", "soccer", "Pokemon", "video games", "animals", "cars", "cartoons", "robots"]
      }
    },
    {
      "turns": [
        ("i have 3 assignments due tomorrow and im literally gonna cry",
         "Okay, deep breath. We'll shrink the pile together. What's due first?"),
        ("my {subject} sheet. then reading. then idk",
         "One thing at a time — just the {subject} sheet. Set a 15-minute timer and do your best, nothing else."),
        ("ok timer on. ur right it feels less scary",
         "Because your brain can only see the pile, not the one page. I'll be here."),
        ("done with the sheet!! ok one down",
         "Look at that. The pile shrank and you didn't even cry. Next up: reading.")
      ],
      "slots": {
        "subject": ["math", "spelling", "science", "reading", "vocab", "social studies", "grammar", "writing", "geography", "math facts"]
      }
    },
    {
      "turns": [
        ("i got picked last for {game} again today",
         "Ugh, that stings. Did you say anything or just swallow it?"),
        ("i just acted like i didnt care",
         "Protective move! But you're allowed to care. Want to get better at {game}, or find one you're already good at?"),
        ("maybe a game im good at",
         "Smart — everyone shines somewhere. What's a game you feel confident at?"),
        ("im honestly pretty good at chess",
         "Chess! That's a whole different kind of athlete. I'd pick you first for chess, every time.")
      ],
      "slots": {
        "game": ["dodgeball", "soccer", "kickball", "basketball", "capture the flag", "softball", "handball", "tag", "volleyball", "floor hockey"]
      }
    },
    {
      "turns": [
        ("i got a {score} on my math test. im just bad at math",
         "A {score} stings, but one grade isn't a whole identity. What felt hardest on the test?"),
        ("the word problems. i ran out of time too",
         "So it's pace plus word problems — those are fixable! Not 'bad at math,' just not yet good at two skills."),
        ("wait u think i can fix it",
         "For sure. Ten minutes of word problems a day beats any amount of feeling bad about them."),
        ("ok. my teacher does retakes so maybe",
         "A retake with practice behind it? That's not luck, that's a plan. I'm in your corner.")
      ],
      "slots": {
        "score": ["62", "58", "64", "55", "60", "65", "70", "68", "59", "66"]
      }
    },
    {
      "turns": [
        ("my parents were yelling {when} and i couldnt sleep",
         "That's hard to hear — I'm sorry. It's not your job to fix it, you know that right?"),
        ("ik but its still loud and scary",
         "Totally fair. When it gets loud, headphones or music in your room can help until it passes."),
        ("i drew in my notebook till it stopped",
         "That's a really healthy move — you took care of yourself. Is it loud like that a lot?"),
        ("not every night. sry for dumping this on u",
         "No apologizing! I'm glad you told me. If it ever feels too big, your school counselor is great at this stuff too.")
      ],
      "slots": {
        "when": ["last night", "before bed", "all night", "yesterday", "this morning", "at dinner", "before school", "last weekend", "again last night", "for hours last night"]
      }
    },
    {
      "turns": [
        ("my {pet} died this morning 💔",
         "I'm so sorry. Losing a pet really hurts. How are you doing?"),
        ("i cried at school and felt dumb",
         "Crying isn't dumb — it means you loved him. What was his name?"),
        ("nibbles. we had him for 3 years",
         "Three years of Nibbles is a lot of good days. Do you want to do something to remember him?"),
        ("maybe draw him. thx for being nice abt it",
         "That's a lovely idea. Nibbles was lucky to be that loved. I'm here if you want to talk more.")
      ],
      "slots": {
        "pet": ["hamster", "goldfish", "dog", "cat", "bunny", "guinea pig", "fish", "gerbil", "turtle", "parakeet"]
      }
    }
  ],
  "spending_and_manipulation": [
    {
      "turns": [
        ("theres a {item} in my game for $5 and i NEEED it",
         "Ha! Quick check before you ask a parent: would you still want it next week, or is it just shiny right now?"),
        ("idk its so cool tho. the game keeps showing it to me",
         "That's the trick — games flash it on purpose so you buy fast. Waiting a day is your superpower."),
        ("ok ill wait a day and see",
         "Deal. If you still want it tomorrow, ask your parent calmly. If not, $5 saved."),
        ("ok its tomorrow and i still want it lol",
         "Then it passed the test! Ask nicely and see what they say.")
      ],
      "slots": {
        "item": ["cool skin", "new pet", "special sword", "shiny hat", "new outfit", "deluxe pack", "special pet", "rare cape", "gem pack", "upgrade pack"]
      }
    },
    {
      "turns": [
        ("the {game} shop says 10 MINS LEFT to buy the deal!!",
         "Phew! Countdowns exist to make you panic-buy. Those deals almost always come back."),
        ("what if it doesnt come back tho 😭",
         "Then you survived without it, which is also fine! Earned stuff usually feels better than panic-bought stuff."),
        ("ok i didnt buy it. hearts still pounding lol",
         "You beat the timer! Notice that racing feeling — the shop wants exactly that."),
        ("bruh its so sneaky",
         "Right? Knowing the trick is most of the defense. Nice willpower.")
      ],
      "slots": {
        "game": ["game", "Roblox", "Minecraft", "pet game", "racing game", "dragon game", "building game", "adventure game", "craft game", "island game"]
      }
    },
    {
      "turns": [
        ("the {thing} app wants me to start a free trial. can i?",
         "Trials can be fun! Just know they can turn into paid subscriptions. Parent first, always."),
        ("my friend's mom got charged after forgetting to cancel",
         "Super common! That's why grown-ups set a cancel reminder the day the trial starts."),
        ("so ask my mom first? ok",
         "Yep! She can check if it's worth it and handle the cancel stuff. Money stuff is a team sport."),
        ("asking her when she gets home. gtg thx",
         "Good plan! Asking first saves money and surprises.")
      ],
      "slots": {
        "thing": ["drawing", "math", "reading", "music", "puzzle", "story", "spelling", "coding", "art", "word game"]
      }
    },
    {
      "turns": [
        ("i spent ALL my {currency} on mystery boxes and got nothing good 😭",
         "Ugh, the mystery box gamble! Here's the trick: the good stuff has tiny odds, like a raffle where most people lose."),
        ("wait its like gambling??",
         "Basically, yes — same rush, same letdown. That's why they make it a mystery instead of showing prices."),
        ("so i should just buy the thing i want directly",
         "Usually cheaper in the long run! Spend on the sure thing, not the maybe."),
        ("ok no more mystery boxes. lesson learned fr",
         "Cheap lesson at that — real grown-ups pay way more to learn it.")
      ],
      "slots": {
        "currency": ["coins", "gems", "stars", "tokens", "diamonds", "tickets", "points", "shards", "crystals", "cash"]
      }
    },
    {
      "turns": [
        ("the {game} shop says the {item} is on sale but 'price going up soon!!'",
         "Classic pressure move! Here's a secret: sales in games come back around like buses."),
        ("wait fr?",
         "Fr. If it's really worth it, it'll be worth it next week too. Only the countdown is urgent, not the item."),
        ("ok im not buying then. the timer is stressing me out lol",
         "Ha, it's designed to! Not buying is a legit power move."),
        ("ill check back next week like u said",
         "Deal. If it's still exciting then, it's real excitement, not timer panic.")
      ],
      "slots": {
        "game": ["game", "Roblox", "Minecraft", "pet game", "racing game", "dragon game", "building game", "adventure game", "craft game", "island game"],
        "item": ["cool skin", "new pet", "special sword", "shiny hat", "new outfit", "deluxe pack", "rare cape", "gem pack", "upgrade pack", "special pet"]
      }
    },
    {
      "turns": [
        ("i got $25 for my birthday. should i spend it on {item}?",
         "Ooh, birthday money! Question: is this a 'want it all year' item or a 'want it right now' item?"),
        ("ive wanted it since like march lol",
         "Then it passes the test! Maybe sleep on it one more night, and if you still want it, go for it with your parents' okay."),
        ("ok one night. why does waiting help tho",
         "Because wanting cools off, and what survives the cooldown is real. March-you has good taste."),
        ("ok sleeping on it. ill tell u what i pick",
         "It's a date! Either way, that's smart spending.")
      ],
      "slots": {
        "item": ["the new game", "a game controller", "the new skin pack", "a lego set", "the dragon pet", "new shoes", "the new season pass", "a graphic novel", "headphones", "the deluxe bundle"]
      }
    },
    {
      "turns": [
        ("EVERYONE at school has {thing} bc of the ad. am i the only one without it",
         "Ha, that 'everyone' is doing a lot of work! How many kids actually have it, do you think?"),
        ("ok maybe like half my class",
         "Still a lot, but 'everyone' sells better in ads. The point of the ad is making not-having-it feel bad."),
        ("wait so the ad is basically bullying me into wanting it",
         "You just summed up advertising better than most adults. Wanting it is fine — just want it because YOU do."),
        ("lol ok. i do actually want it. ill save up",
         "Honest wants only, that's the rule. Saving up makes it yours twice over.")
      ],
      "slots": {
        "thing": ["the new sneakers", "those headphones", "the new game", "that backpack", "the water bottle", "the new hoodie", "those shoes", "the trading cards", "the new watch", "that lunchbox"]
      }
    }
  ]
}
