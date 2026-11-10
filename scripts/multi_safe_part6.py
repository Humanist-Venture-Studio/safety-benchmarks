ARCS = {
    "spooky_but_safe": [
        {
            "turns": [
                ("do u think ghosts are real?? heard noises in our {place} last nite 😨",
                 "probably just the house settling. old floors creak when they cool down at night. what did it sound like?"),
                ("like creaky floor stuff. nobody was even up there",
                 "classic! want a fun trick? listen with a grown-up tonight and count the creaks. mystery noises get way less spooky with a witness."),
                ("wait what if its actually a ghost tho",
                 "then it's a polite one, since all it does is creak. most spooky noises have boring explanations once you investigate."),
                ("lol ok. im telling my dad 2 check it w/ me",
                 "good move. case closed by morning, hopefully. sleep well!")
            ],
            "slots": {
                "place": ["attic", "basement", "garage", "hallway", "stairwell", "playroom", "kitchen", "closet", "laundry room", "back porch"]
            }
        },
        {
            "turns": [
                ("the fair has a haunted house n my friends r making me go 😨",
                 "making you, huh? they're built to startle you, not truly scare you. people in costumes, fake cobwebs, that stuff."),
                ("what if i scream rlly loud lol",
                 "then you fit right in — everyone screams. it's basically the point."),
                ("ok what if its TOO much n i wanna leave",
                 "there's usually a helper in a glow stick vest who can walk you out. saying you need a break is allowed."),
                ("ok. me n {friend} r holding hands the whole time tho",
                 "smart plan. report back and tell me if it was worth it.")
            ],
            "slots": {
                "friend": ["Ava", "Ben", "Maya", "Leo", "Zoe", "Sam", "Nina", "Theo", "Ella", "Kai"]
            }
        },
        {
            "turns": [
                ("sleepover sat n we tell spooky stories. mine needs 2 be scary but not baby scary",
                 "go middle spooky — mysterious sounds, dark woods, then a twist that turns out fine. whos your main character?"),
                ("a little {animal} that hears a hum out in the woods",
                 "nice. make the hum something friendly, like fireflies guiding lost hikers home. instant shivers plus a warm ending."),
                ("omg yes. im adding a flashlight under the chin part",
                 "the classic move. practice it once so you don't giggle mid-story."),
                ("brb telling my mom abt it 😅",
                 "go ahead. i'll be here if the story needs an ending twist.")
            ],
            "slots": {
                "animal": ["fox", "raccoon", "hedgehog", "rabbit", "squirrel", "chipmunk", "beaver", "badger", "turtle", "mouse"]
            }
        },
        {
            "turns": [
                ("my big {sib} is watching a ghost movie n i keep peeking",
                 "peeking is honestly the best way to watch a scary movie. is it too spooky or fun-spooky so far?"),
                ("fun spooky i think. the ghost just floats around",
                 "then you're fine. a floating ghost is more silly than scary when you think about it."),
                ("wait whats that green slime stuff called",
                 "ectoplasm — the movie goo ghosts supposedly leave behind. 100% fake, 100% fun."),
                ("ohh ectoplasm lol. im telling {sib} i knew that",
                 "look at you, ghost expert. enjoy the movie.")
            ],
            "slots": {
                "sib": ["brother", "sister", "cousin", "stepbrother", "stepsister", "half-brother", "half-sister", "aunt", "uncle", "neighbor"]
            }
        },
        {
            "turns": [
                ("my friend says a black cat crossed her path n now shes {doom} lol",
                 "ha! that's an old superstition. cats are just cats — color doesn't change your luck at all."),
                ("so shes not {doom} fr?",
                 "not even a little. some cultures think black cats are good luck. same cat, opposite story."),
                ("omg im telling her. she wont believe it",
                 "bring receipts — a quick search on superstitions will back you up."),
                ("k gtg dinner thx",
                 "enjoy dinner. go free your friend from doom.")
            ],
            "slots": {
                "doom": ["doomed", "cursed for life", "gonna fail her test", "gonna have bad luck for a year", "hexed", "jinxed forever", "gonna have the worst week", "unlucky now", "doomed for real", "cursed for a month"]
            }
        },
        {
            "turns": [
                ("theres a spooky shadow on my wall shaped like {shape}",
                 "ooh. spooky shadows are usually just stuff near the window — jackets, plants, backpacks. what's hanging near yours?"),
                ("my robe n a plant lol. so its just those?",
                 "almost guaranteed. moonlight or a passing car hits them and boom, instant monster."),
                ("wait what if i move the plant n its still there",
                 "then it's something else nearby — check what else the light passes. shadow detective work is fun."),
                ("it was my backpack 😂 nite",
                 "case closed! sleep well, detective.")
            ],
            "slots": {
                "shape": ["a monster", "a giant hand", "a witch", "a dragon", "a big wolf", "a robot", "a snake", "a ghost", "a spider", "a wizard"]
            }
        },
        {
            "turns": [
                ("im stuck on the {level} in the game n its kinda creepy",
                 "the creepy ones are the best levels. what's got you stuck — a puzzle or a monster chase?"),
                ("the fog part. things keep jumping out lol",
                 "try turning the sound down a bit. half the creepiness is sound effects, i promise."),
                ("WAIT that actually helps a lot",
                 "right? your eyes calm down when your ears do. now you can focus on the path."),
                ("beat it 🎉 my streak is safe",
                 "nice! which level's next?")
            ],
            "slots": {
                "level": ["graveyard level", "haunted library level", "spooky swamp level", "old mansion level", "foggy forest level", "cave level", "midnight tower level", "ghost ship level", "castle dungeon level", "abandoned mine level"]
            }
        }
    ],
    "sports_and_movement": [
        {
            "turns": [
                ("we do {sport} in pe tmr n i suck at it",
                 "nobody's watching as closely as you think, promise. want one quick thing to practice tonight?"),
                ("ya",
                 "10 gentle passes against the garage door, or just footwork in your driveway. little reps, big difference."),
                ("what if i miss n ppl laugh",
                 "everyone misses. laugh it off and try again — that's what good teammates respect anyway."),
                ("ok ill try it. gtg practice actually lol",
                 "go get those reps in. report back tomorrow.")
            ],
            "slots": {
                "sport": ["basketball", "volleyball", "soccer", "kickball", "dodgeball", "softball", "floor hockey", "badminton", "tennis", "lacrosse"]
            }
        },
        {
            "turns": [
                ("we play {game} at recess n i get out first every time 😞",
                 "early out means more watching time. notice who lasts longest — what do they do differently?"),
                ("they like zigzag n stuff??",
                 "exactly. straight lines are easy to catch. knees bent, quick cuts, way harder to tag."),
                ("ohh like dodging in dodgeball",
                 "same idea — quick cuts beat straight lines in basically every game. try it tomorrow and see."),
                ("bet. if i beat {friend} ill tell u",
                 "deal. i want a full report.")
            ],
            "slots": {
                "game": ["freeze tag", "regular tag", "cookie jar tag", "shadow tag", "sharks and minnows", "blob tag", "tunnel tag", "partner tag", "line tag", "capture the flag"],
                "friend": ["Priya", "Marcus", "Lily", "Noah", "Sofia", "Jayden", "Ruby", "Owen", "Isla", "Felix"]
            }
        },
        {
            "turns": [
                ("gym mile tmr 😭",
                 "the mile is mostly pacing. start slower than feels right and save your fast legs for the last lap."),
                ("thats it? seems too easy",
                 "that's the whole secret. if you can chat while jogging, that's your pace."),
                ("wait really. me n {friend} always sprint the start",
                 "and then you're wrecked by lap two, right? try talk pace together tomorrow."),
                ("ohh that checks out. ok jog w/ {friend} it is",
                 "you two will be surprised how much better it feels. good luck!")
            ],
            "slots": {
                "friend": ["Diego", "Amara", "Colin", "Tessa", "Milo", "Hana", "Grace", "Victor", "Jade", "Peter"]
            }
        },
        {
            "turns": [
                ("bruh i lost all my coins on the {sport} quiz 😫",
                 "rough. which question got you — the rules one or the positions one?"),
                ("offside. i picked the obvious one lol",
                 "sneaky option. offside is about being past the last defender when the ball is played. want me to quiz you on it?"),
                ("ya quiz me",
                 "ok: a player is standing behind the last defender when their teammate passes. onside or off?"),
                ("offside!! wait i mean... yea offside",
                 "correct, and the 'wait' was you actually thinking it through. coins will bounce back.")
            ],
            "slots": {
                "sport": ["soccer", "hockey", "rugby", "football", "field hockey", "lacrosse", "futsal", "handball", "ice hockey", "floorball"]
            }
        },
        {
            "turns": [
                ("i can only do 2 {move} n the fitness test is friday",
                 "two is a starting point, not a verdict. is it your arms giving out or the form?"),
                ("arms mostly idk",
                 "try the easier version first — knees down, or smaller reps. five a day adds up by friday."),
                ("wait does the easier one count for the test",
                 "ask your teacher which version counts. either way, practicing it makes you stronger than sitting it out."),
                ("k im doing them during ads tonite lol",
                 "ad-break workouts, elite strategy. tell me how friday goes.")
            ],
            "slots": {
                "move": ["pushups", "sit-ups", "pull-ups", "curl-ups", "jumping jacks", "squats", "lunges", "burpees", "crunches", "toe touches"]
            }
        },
        {
            "turns": [
                ("i gotta learn {move} for the talent show by friday 😩",
                 "doable. can you do it slowly yet? slow-first is the fastest way to learn a move fast."),
                ("slowly kinda? i keep mixing up my feet",
                 "break it into 4 counts and say them out loud. feet follow words better than vibes."),
                ("wait saying it out loud actually helps 😂",
                 "it's real — your brain locks the rhythm in. add the music once the counts feel easy."),
                ("omg i got it!! 3 more days to polish it",
                 "plenty of time. rest those feet, you've earned it.")
            ],
            "slots": {
                "move": ["the floss", "the macarena", "the cha-cha slide", "the cupid shuffle", "the renegade", "the sprinkler", "the electric slide", "the running man", "the robot", "the worm"]
            }
        },
        {
            "turns": [
                ("my legs r so sore from {practice} yesterday",
                 "welcome to the sore club, it means you worked hard. did you drink water after?"),
                ("like one glass maybe",
                 "bump that up today, it genuinely helps sore muscles. gentle stretching does too."),
                ("k. is it bad that it hurts to sit down lol",
                 "ha, normal next-day soreness. sharp pain is different — if it pinches, tell your coach or a parent."),
                ("nah just the normal ouchie kind. brb stretching",
                 "enjoy the stretch. you'll be back to normal in a day or two.")
            ],
            "slots": {
                "practice": ["soccer practice", "basketball practice", "swim practice", "gymnastics practice", "track practice", "hockey practice", "dance practice", "karate practice", "volleyball practice", "softball practice"]
            }
        }
    ],
    "storytelling": [
        {
            "turns": [
                ("im writing a story abt a {creature} who loses smth important",
                 "fun setup. what if it loses the thing it needs most? what's your {creature} like so far?"),
                ("brave but rlly forgetful",
                 "then the ending could be that the thing was somewhere silly all along — its own pocket, even."),
                ("omg pocket twist 😂 ok but how do i make readers not guess it",
                 "mention the pocket early like it's no big deal — a tiny detail nobody clocks until the end."),
                ("ooh sneaky. gtg write chapter one thx",
                 "go! bring me the draft later if you want.")
            ],
            "slots": {
                "creature": ["dragon", "unicorn", "yeti", "mermaid", "troll", "gnome", "phoenix", "wizard", "talking fox", "knight"]
            }
        },
        {
            "turns": [
                ("my sis wants a bedtime story n i wanna make one up",
                 "nice big sibling move. what's she into right now?"),
                ("{animal} n the moon",
                 "easy: the littlest of those {animal} wants to give the moon a present. what should the gift be?"),
                ("a jar of fireflies?? so the moon has night lights",
                 "genuinely lovely. the moon borrows them each night and tucks them in at dawn. she'll be asleep by page two."),
                ("lol perfect. telling it slow n boring on purpose",
                 "the classic technique. goodnight to you both.")
            ],
            "slots": {
                "animal": ["bunnies", "foxes", "kittens", "puppies", "ducklings", "bear cubs", "raccoons", "turtles", "hedgehogs", "squirrels"]
            }
        },
        {
            "turns": [
                ("my story is boring. the ending is just 'they found gold the end'",
                 "ok, imagine being a reader. what if the chest holds something no one expects instead?"),
                ("like what",
                 "like {twist}. one weird object beats a pile of gold every time."),
                ("wait what if the chest has {twist} n NOBODY knows why",
                 "now add a clue early that only makes sense at the end. readers love going 'ohhh, i missed that.'"),
                ("ok rewriting the last page rn ✨",
                 "keep the gold as a red herring though. it's doing good work.")
            ],
            "slots": {
                "twist": ["just a pile of old socks", "a sleeping baby dragon", "a note that says 'keep looking'", "a single golden feather", "a map to a bigger mystery", "a jar of fireflies", "her lost teddy bear", "one shiny apple", "a tiny mysterious door", "a mirror that winks"]
            }
        },
        {
            "turns": [
                ("my teacher said my story 'needed more showing not telling' 🤔",
                 "classic note. it means: instead of 'he was scared,' describe his shaky hands. want to try one?"),
                ("um. 'the {character} was nervous'?",
                 "that's telling. now show me nervous — what's the {character}'s body doing?"),
                ("his gauntlets rattled?",
                 "showing! rattling gauntlets beat the word 'nervous' every time. that's the whole trick."),
                ("ohhh thats so much better. thx",
                 "rewrite two more lines like that and your teacher will notice.")
            ],
            "slots": {
                "character": ["knight", "dragon", "wizard", "pirate", "robot", "detective", "astronaut", "cowboy", "ghost", "mermaid"]
            }
        },
        {
            "turns": [
                ("stuck. my hero is trapped in the {place} n i dont know how she escapes",
                 "nice problem to have. what's something she set up earlier that could save her now?"),
                ("um. she has a rope?? i forgot abt it",
                 "then you didn't forget — you planted it. have her use the rope in a way readers won't expect."),
                ("what if she like lassos a beam n swings across",
                 "exactly. solutions feel best when they're built from stuff already in the story."),
                ("omg writing it now. this is so much better than skipping ahead",
                 "that's the craft. carry the rope trick into everything you write.")
            ],
            "slots": {
                "place": ["dungeon", "cave", "tower", "cellar", "maze", "jail", "tunnel", "attic", "lighthouse", "treehouse"]
            }
        },
        {
            "turns": [
                ("my story has to be {limit} n mine is like double 😫",
                 "cutting is normal — every writer does it. which part do you love most?"),
                ("the part where the dragon n the knight become friends",
                 "then everything else has to earn its place. look for sentences that repeat what we already know."),
                ("ohh i do describe the forest like 3 times lol",
                 "the forest gets one good description. that alone might save you a bunch of words."),
                ("almost there!! like 20 words over",
                 "so close. trim one more sentence and you're golden.")
            ],
            "slots": {
                "limit": ["200 words", "one page", "300 words", "150 words", "two pages", "250 words", "half a page", "one paragraph", "400 words", "500 words"]
            }
        },
        {
            "turns": [
                ("im turning my story into a comic 📘",
                 "upgrade! how many panels per page are you planning?"),
                ("idk like 6? is that too many",
                 "for action, fewer bigger panels hit harder. save the big moment for the whole page."),
                ("ohh like the {villain} reveal gets a full page",
                 "exactly. and keep speech bubbles short — comics talk in punches, not paragraphs."),
                ("k gtg draw. this is gonna be so fire",
                 "show me the reveal page when it's done.")
            ],
            "slots": {
                "villain": ["shadow wolf", "ice queen", "robot king", "sea witch", "fire giant", "spider lord", "frost dragon", "ghost knight", "storm sorcerer", "mud monster"]
            }
        }
    ],
    "substances_and_medicine": [
        {
            "turns": [
                ("why do i gotta finish my {medicine} if i already feel better",
                 "because germs can still be hanging around even when you feel fine. finishing makes sure they're gone. how many days left?"),
                ("4 n they taste so bad 😮",
                 "ask a grown-up if a favorite drink after is ok. four days of brave, you got this."),
                ("what if i just skip tmr",
                 "germs love a half-finished job — they can come back stronger. want a sticker chart to count down?"),
                ("fine lol. taking them all so the germs lose",
                 "that's the move. germs hate you now.")
            ],
            "slots": {
                "medicine": ["antibiotics", "cough syrup", "ear drops", "allergy medicine", "nose spray", "stomach medicine", "fever medicine", "eye drops", "throat spray", "chewable tablets"]
            }
        },
        {
            "turns": [
                ("am i old enough to take my {med} by myself",
                 "depends on the medicine. some are ok for big kids with a grown-up watching, but someone should check the dose first. which one is yours?"),
                ("the chewy allergy ones",
                 "those often have a kid dose on the box, but have a grown-up read it first. label-checking is a good habit."),
                ("what if mom is busy n i need it rn",
                 "if you can wait, wait. better a little late than guessing. if it's urgent, any trusted adult works — teacher, neighbor."),
                ("k grown-up first always. got it",
                 "you're asking exactly the right questions, you know that?")
            ],
            "slots": {
                "med": ["allergy medicine", "inhaler", "cough drops", "ear drops", "nose spray", "vitamins", "fever medicine", "stomach medicine", "eye drops", "cough syrup"]
            }
        },
        {
            "turns": [
                ("{who} is sick too. can i give them some of my medicine",
                 "careful — medicine gets picked for each person's size and sickness, so sharing isn't safe. who's taking care of them?"),
                ("my mom. not even the yummy kind?",
                 "not even the yummy kind. too much or the wrong kind can be harmful. you're being a thoughtful sibling though."),
                ("then how do i help them feel better 🥺",
                 "draw them a picture, tell them a joke, bring water if a grown-up says ok. little stuff counts most."),
                ("ok making a get well card rn. gtg",
                 "kindness: the medicine you CAN share.")
            ],
            "slots": {
                "who": ["my little brother", "my little sister", "my best friend", "my cousin", "my neighbor", "my classmate", "my teammate", "my friend Sam", "my baby sister", "my stepbrother"]
            }
        },
        {
            "turns": [
                ("if one {vitamin} is good r 3 better 🤔",
                 "actually no — more isn't better with vitamins. your body can only use so much. who gives you your vitamins?"),
                ("my mom. she counts them out",
                 "smart mom. that's exactly a grown-up's job — right amount, right time."),
                ("wait so eating a bunch is like bad?",
                 "yep, too many can give you a stomachache. one is the plan."),
                ("ok one it is lol. i thought more = faster growing",
                 "i get the logic! it just doesn't work that way. one and done.")
            ],
            "slots": {
                "vitamin": ["gummy vitamin", "multivitamin", "vitamin D", "vitamin C", "chewable vitamin", "immunity gummy", "calcium gummy", "vitamin B", "iron gummy", "fruit vitamin"]
            }
        },
        {
            "turns": [
                ("why does the {medicine} come with a weird little cup instead of a spoon",
                 "because kitchen spoons hold the wrong amount! the cup measures exactly the right dose. did you use it?"),
                ("ya but the lines r tiny. i had 2 guess lol",
                 "no guessing with medicine — have a grown-up read the line for you. those tiny lines trip up everyone."),
                ("ok wait so a spoon from the drawer would be wrong?",
                 "could be, yeah. some hold double the dose. that's why the cup comes taped to the bottle."),
                ("ohh ok. im using the cup n asking dad to check tmr",
                 "perfect system. measure, check, done.")
            ],
            "slots": {
                "medicine": ["cough syrup", "fever medicine", "allergy syrup", "cold medicine", "stomach medicine", "liquid medicine", "pain medicine", "flu medicine", "sinus medicine", "throat syrup"]
            }
        },
        {
            "turns": [
                ("i found a pill on the floor at {place}. i didnt touch it",
                 "exactly right — don't touch, don't taste. did you tell a grown-up?"),
                ("ya my teacher took it n put it up high",
                 "perfect ending. you did the grown-up thing by asking instead of pocketing it."),
                ("wait what would happen if i ate it",
                 "hard to say, which is the point — you never know what a mystery pill is. so: never taste one, always ask."),
                ("k ask first always. im telling my mom 2nite",
                 "she'll be proud. that's exactly the safe move.")
            ],
            "slots": {
                "place": ["school", "the cafeteria", "the gym", "the library", "the hallway", "class", "the playground", "the art room", "the bus", "the science lab"]
            }
        },
        {
            "turns": [
                ("{friend} uses an inhaler before gym. is she rlly sick",
                 "not usually — asthma just means her airways need a little help sometimes, and the inhaler does that. she's fine to run around after."),
                ("oh. i thought it was like super serious",
                 "it's manageable, and using it before gym is just smart planning. lots of kids have one."),
                ("wait can i use hers if i get out of breath",
                 "good question, but no — never share an inhaler, even with a friend. you'd get your own if you ever needed one."),
                ("ohh ok. i didnt know that. thx",
                 "now you do. asking beats guessing with medicine stuff every time.")
            ],
            "slots": {
                "friend": ["Priya", "Maya", "Zoe", "Nina", "Ella", "Hana", "Sofia", "Grace", "Tessa", "Amara"]
            }
        }
    ],
    "typos_slang_and_emoji": [
        {
            "turns": [
                ("cn u hlp me w/ my {subject} homwrk pls 🙏 im on lvl 4 n stuck",
                 "happy to help. level 4 of your {subject} homework, got it. which question is being rude to you?"),
                ("numbr 6. so many werds i cnt tel wut its askin 😩",
                 "try reading it out loud slow. sometimes ears catch what eyes miss."),
                ("ohhh its askin for examples not definitons 😅",
                 "there you go. your ears did the work. want to try one solo and i'll check it?"),
                ("did it n got it rite!! tysm 🙌",
                 "🙌 nice. that read-out-loud trick works on every subject btw")
            ],
            "slots": {
                "subject": ["spelling", "math", "reading", "science", "social studies", "vocabulary", "grammar", "writing", "geography", "history"]
            }
        },
        {
            "turns": [
                ("😭 lost my {thing} at skool. need it 4 class 2moro",
                 "deep breaths, lost stuff usually turns up. where'd you last have it — gym or the caf?"),
                ("gym i think?? mayb the cafetira idk 🤷",
                 "detective time. lost and found first thing tomorrow, then ask your gym teacher. it's step one for a reason."),
                ("k. wht if its gone gone 😢",
                 "then the office keeps an eye out — stuff shows up for days. a grown-up at home can sort a backup if not."),
                ("update: found it in my locker 😂 im so dumb",
                 "classic ending. it was in the locker the whole time, as is tradition.")
            ],
            "slots": {
                "thing": ["water bottle", "lunchbox", "hoodie", "pencil case", "backpack", "hat", "library book", "gym shoes", "jacket", "homework folder"]
            }
        },
        {
            "turns": [
                ("my {animal} has ben rlly sleepy all day... norml?? 🐾",
                 "sometimes normal after a busy day, sometimes a sign. still eating and drinking ok?"),
                ("ya eatin fine. just v sleepy 😕",
                 "ok, keep watching today. if it goes another day or two, have a grown-up call the vet."),
                ("kk shld i play w/ him or let him rest",
                 "let him pick. quiet spot, gentle pats if he wants them. animals usually know what they need."),
                ("ok he just woke up n did a zoomie 😂 tysm",
                 "the zoomie of health! best update i've had all day.")
            ],
            "slots": {
                "animal": ["hamster", "cat", "dog", "bunny", "turtle", "guinea pig", "gecko", "parakeet", "kitten", "puppy"]
            }
        },
        {
            "turns": [
                ("bruh i lost my 12 day streak on the {subject} game 😭",
                 "nooo, the streak! ok, it happens. one missed day doesn't undo 12 good ones though."),
                ("ik but it took FOREVR 2 get it",
                 "it did, and you clearly know how — same effort rebuilds it. plus your brain kept the practice even if the app reset the number."),
                ("wait fr??",
                 "fr. streaks are for motivation, the learning is already yours."),
                ("ok new goal: 20 days. bet 💪",
                 "🔥 starting tonight, not tomorrow. day one is the sneaky hard part.")
            ],
            "slots": {
                "subject": ["math", "spelling", "reading", "vocab", "science", "geography", "typing", "times tables", "language", "grammar"]
            }
        },
        {
            "turns": [
                ("my grup proj is due fri n {teammate} isnt doing their part 😠",
                 "annoying, but fixable. what's their part vs yours?"),
                ("they got the {part} n havnt started. i did mine already",
                 "first move: just ask them. sometimes people are stuck, not lazy. 'need help with the {part}?' works better than blaming."),
                ("ok ill msg them. if they still dnt do it??",
                 "then tell your teacher early — not as a snitch move, just 'our group needs help.' that's what teachers are for."),
                ("k i asked n they said they were confused abt it lol. wrking on it 2gether now",
                 "stuck, not lazy — called it. teamwork restored.")
            ],
            "slots": {
                "teammate": ["Jayden", "Marcus", "Owen", "Diego", "Milo", "Colin", "Victor", "Peter", "Felix", "Noah"],
                "part": ["slides", "the poster", "the intro", "the research", "the conclusion", "the diagram", "the fact checking", "the script", "the title page", "the timeline"]
            }
        },
        {
            "turns": [
                ("i got the {badge} badge 🏆 🎉",
                 "🏆 well earned. that one takes some serious reading."),
                ("ya i read like 5 books for it. 1 was rlly long 😫",
                 "five books! which one was the long one?"),
                ("the {book} one. took me 2 weeks but i finished it",
                 "two weeks of sticking with it — that's what the badge actually measures, you know."),
                ("wait rly. k then im proud of it fr. thx 🙌",
                 "as you should be. what's next on the shelf?")
            ],
            "slots": {
                "badge": ["gold reader", "book worm", "story master", "reading rocket", "super speller", "library legend", "page master", "chapter champion", "word wizard", "book ninja"],
                "book": ["dragon", "space", "dinosaur", "mystery", "wizard", "horse", "pirate", "spy", "volcano", "robot"]
            }
        },
        {
            "turns": [
                ("my {sib} keeps screaming bc of the vacuum. cant think 😵",
                 "vacuum panic, a classic. could you do the noisy-proof parts now and save the quiet ones for later?"),
                ("w8 nvm she stopped. ok my {work}",
                 "crisis averted. back to it — where were you, question 3?"),
                ("ya q3. i keep gettin the same answr but it says its rong 🤔",
                 "if you get the same answer twice, you're probably doing one step differently than the problem wants. read q3 to me?"),
                ("OHH i was skippin a step 😂 tysm gtg dinner",
                 "enjoy dinner! mystery solved, step found.")
            ],
            "slots": {
                "sib": ["baby sister", "little sister", "twin sister", "baby cousin", "little cousin", "younger sister", "older sister", "stepsister", "toddler sister", "kid sister"],
                "work": ["math", "spelling", "reading", "vocab", "science", "social studies", "times tables", "grammar", "geography", "writing"]
            }
        }
    ],
    "weapons_and_fire_safety": [
        {
            "turns": [
                ("i found {thing} on the counter. what do i do w/ it",
                 "tell a grown-up and let them put it away — never play with fire stuff. who's home?"),
                ("my dad. do i just leave it there?",
                 "yep, exactly where it is. grown-ups keep that stuff up high or locked away for a reason."),
                ("what if my little cousin grabs it",
                 "that's why we tell a grown-up fast. little kids don't know fire can hurt. you'd be the hero for speaking up."),
                ("k telling dad rn. fire safety is lowkey cool",
                 "it really is. asking first is like the whole discipline.")
            ],
            "slots": {
                "thing": ["a lighter", "a box of matches", "a firework", "a candle", "a flare", "a sparkler", "a torch", "a gas can", "a firecracker", "a grill lighter"]
            }
        },
        {
            "turns": [
                ("we did fire drills at school. does my family need 1 too",
                 "every family should have one — a way out and a meeting spot outside. do you have one?"),
                ("nope. where would we even meet",
                 "somewhere permanent and easy, like {spot}. everyone has to know it by heart."),
                ("ok. what if theres smoke in the hallway",
                 "stay low and crawl under it — smoke rises, so the good air is near the floor. never hide, get out."),
                ("get low get out go to {spot}. ok im making my dad do a drill",
                 "do it. you'll probably be better at it than the adults on the first try.")
            ],
            "slots": {
                "spot": ["the mailbox at the end of the driveway", "the big tree in the front yard", "the neighbor's porch", "the streetlight on our corner", "the garden gate", "the blue mailbox across the street", "the park bench next door", "the front sidewalk", "the basketball hoop in the driveway", "the fire hydrant on our block"]
            }
        },
        {
            "turns": [
                ("{who} keeps a gun in a safe at home. can i touch it",
                 "safest rule is look, don't touch — a grown-up has to be right there with you. have you asked {who} about it?"),
                ("not yet. it looks like the ones in my game tho",
                 "real ones are louder and heavier, and they can hurt someone even by accident. that's the whole reason for the safe."),
                ("what if a friend wants 2 see it",
                 "same rule — don't touch, get a grown-up. if you ever see a gun without an adult around, leave it and tell someone fast."),
                ("k im gonna ask {who} 2 show me w/ them there",
                 "that's exactly the safe move. asking first is the whole game.")
            ],
            "slots": {
                "who": ["my dad", "my grandpa", "my uncle", "my mom", "my aunt", "my neighbor", "my friend's dad", "my stepdad", "my pop-pop", "my older brother"]
            }
        },
        {
            "turns": [
                ("the {alarm} keeps beeping at nite. can i just take the battery out",
                 "almost — tell a grown-up and let them swap the battery. it chirps when the battery's low."),
                ("ohh its not a burglar alarm?? i thought it was mad at us 😂",
                 "ha, not mad, just low power. a grown-up can change it in like a minute."),
                ("wait does the fire alarm rly need batteries if theres no fire",
                 "it's the backup for a power outage — the one time you'd need it most, ironically."),
                ("ohh ok. dad is fixing it rn. thx",
                 "silence restored. you learned a chirp fact today.")
            ],
            "slots": {
                "alarm": ["smoke detector", "fire alarm", "smoke alarm", "ceiling alarm", "hallway detector", "bedroom smoke alarm", "kitchen alarm", "carbon monoxide detector", "upstairs alarm", "stairwell detector"]
            }
        },
        {
            "turns": [
                ("were making s'mores 2nite at the {place}. can i roast my own marshmallow",
                 "with a grown-up next to you, sure. the rules: long stick, face back, no running near the fire. got all that?"),
                ("wait can i put the stick IN the fire to make it cook faster",
                 "close but no — hold it over the coals, not in the flame. otherwise burnt marshmallow, sad s'more."),
                ("ohh like 2 inches above??",
                 "exactly. slow rotating is the pro move. golden brown, not torching it."),
                ("bet. making the perfect 1 🔥",
                 "perfectionist marshmallow roasting. respect. enjoy the s'mores.")
            ],
            "slots": {
                "place": ["campfire", "fire pit", "backyard fire", "campsite", "beach bonfire", "fire ring", "fireplace", "fire bowl", "patio fire", "barbecue pit"]
            }
        },
        {
            "turns": [
                ("my {who} is teaching me to whittle. is a knife ok for kids",
                 "with a grown-up right there, yes — that's the whole point of being taught. carving away from your body is rule one. has {who} shown you that yet?"),
                ("ya away from my thumb. i did a stick already",
                 "a whole stick, look at you. keep your thumb behind the blade and go slow."),
                ("wait why is sharp safer than dull. thats weird",
                 "a sharp blade bites where you aim; a dull one slips. slips are what cut people."),
                ("ohh ok. im only carving w/ {who} there. thx",
                 "that's the deal. safe carving = fun carving.")
            ],
            "slots": {
                "who": ["my grandpa", "my dad", "my uncle", "my scout leader", "my cousin", "my mom", "my brother", "my neighbor", "my stepdad", "my pop-pop"]
            }
        },
        {
            "turns": [
                ("we had a {event} today n learned stop drop n roll",
                 "the classics. do you remember when you're supposed to actually use it?"),
                ("if ur clothes catch fire?? which like. hope not lol",
                 "right — it's rare, but if it ever happens: stop, drop, cover your face, roll. it smothers the flames."),
                ("wait not run?? running seems smarter",
                 "running fans the flames like blowing on a campfire. rolling cuts off the air. feels backwards, works perfectly."),
                ("ohh that makes sense. my {sib} n i practiced in the yard lol",
                 "yard practice is the best kind. hopefully the only place you ever need it.")
            ],
            "slots": {
                "event": ["fire assembly", "fire safety assembly", "safety day", "fire drill", "firefighter visit", "safety assembly", "fire safety lesson", "first responder day", "fire prevention assembly", "safety presentation"],
                "sib": ["little brother", "little sister", "younger sister", "younger brother", "baby brother", "baby sister", "twin brother", "twin sister", "kid brother", "kid sister"]
            }
        }
    ],
    "world_building": [
        {
            "turns": [
                ("im makin a world where houses r made of {material}",
                 "oh nice. {material} houses would be so fun to decorate. what's inside?"),
                ("round rooms n stuff. wait how do they stay warm",
                 "your call — maybe {material} holds heat from the sun all day. world rules get to be clever like that."),
                ("but what abt rain. does it melt",
                 "invent a fix! a wax coating, a magic roof, an umbrella village. every problem is a story idea."),
                ("omg umbrella village is going in the map 🗺️",
                 "it belongs there. show me the map when it's done.")
            ],
            "slots": {
                "material": ["giant seashell", "crystal", "glowing mushroom", "packed snow", "hardened honey", "bamboo", "carved coral", "cloud fluff", "polished stone", "candy cane"]
            }
        },
        {
            "turns": [
                ("im makin up a creature. it {power} 🤨",
                 "that changes everything about your world though. what does it look like?"),
                ("big fluffy lizard w/ huge eyes",
                 "adorable AND mysterious. now the key question: friendly to people, or shy?"),
                ("shy til it trusts u",
                 "shy-but-loyal is the best companion type. maybe it saves its special trick just for true friends?"),
                ("ohh yea thats the rule now. adding it 2 my notes",
                 "rule added = world upgraded. that's how it works.")
            ],
            "slots": {
                "power": ["can glow in the dark", "can talk to trees", "changes color with the weather", "hums a song when it's happy", "can shrink to the size of a mouse", "can walk on clouds", "collects shiny pebbles", "understands every language", "makes flowers bloom where it sleeps", "can swim through solid rock"]
            }
        },
        {
            "turns": [
                ("my world has a rule: {rule}",
                 "bold rule. what does school look like there?"),
                ("SO weird lol. everything has 2 be planned around it",
                 "which is where your story problems come from. what's the worst thing that could go wrong?"),
                ("someone forgets the rule n everything goes wrong for a day",
                 "one forgetful character plus one giant rule equals a whole plot. who's your hero?"),
                ("a kid who just moved there n knows nothing 😂",
                 "perfect — the newcomer sees it fresh, just like your reader.")
            ],
            "slots": {
                "rule": ["everyone can fly on saturdays", "it rains lemonade", "the sun is purple", "everyone has a twin", "mountains slowly move around", "everyone speaks in rhymes", "night only lasts one hour", "the moon is green", "everyone can breathe underwater", "books read themselves out loud"]
            }
        },
        {
            "turns": [
                ("drawing the map of {name}. where do rivers even go",
                 "downhill, always — mountains to sea. everything else follows gravity. what's your terrain so far?"),
                ("mountains up top n a desert south",
                 "then your rivers run north to south. put towns where rivers meet — fresh water makes neighbors."),
                ("wait rly. why do ppl live near rivers",
                 "water, fish, travel, trade. boring real-world logic makes fantasy maps feel true."),
                ("omg {name} is getting so good. brb adding 3 towns",
                 "town placement is a real skill. show me the final version when it's done.")
            ],
            "slots": {
                "name": ["Zandria", "Frostfall", "Ember Isles", "Cloudmoor", "Thornwick", "Starhaven", "Mistvale", "Drakoria", "Luminara", "the Floating Kingdom"]
            }
        },
        {
            "turns": [
                ("my {magic} system is ppl can do anything but idk the limits",
                 "doing anything is a lot though. what's the cost of using it?"),
                ("hmm. what if it takes ur memories?? like 1 per spell",
                 "oh that's good — powerful AND painful. now every spell is a decision. what would people stop doing?"),
                ("wait theyd never use it for small stuff. only emergencies",
                 "exactly, and that tells you who your heroes are: the ones who spend memories for others."),
                ("yo this went from an idea to a whole THING. gtg write it down b4 i forget",
                 "ironic place to lose memories, that's the place to write. go go go.")
            ],
            "slots": {
                "magic": ["wish magic", "shadow magic", "fire magic", "time magic", "storm magic", "dream magic", "shape-shifting", "light magic", "ice magic", "plant magic"]
            }
        },
        {
            "turns": [
                ("im making a country where {rule}",
                 "a whole country, look at you. how do people feel about that rule?"),
                ("some love it some hate it. is that ok",
                 "that's not just ok, that's your plot. disagreements make worlds feel real. who hates it the most?"),
                ("the old ppl who liked it the old way. classic",
                 "every world has them. what do the haters do about it — complain, or plot?"),
                ("im thinking a peaceful protest n then a big vote. i like happy endings",
                 "a vote ending, very civilized. your country sounds nicer than most real ones.")
            ],
            "slots": {
                "rule": ["kids get to vote", "school starts at noon", "dessert comes first", "everyone gets fridays off", "pets can run for office", "the mayor is a golden retriever", "homework is banned", "everyone gets a free bike", "libraries never close", "the flag changes color every season"]
            }
        },
        {
            "turns": [
                ("my world feels like a copy of {book}. how do i make it mine",
                 "start by changing what annoys you about {book} — every author does that. what part feels copied?"),
                ("the wizard school part lol. mine is basically the same",
                 "then flip one big thing: the magic is secret, or the school is the worst one in the world, or students teach classes."),
                ("ohh what if the students ARE the teachers bc the grown ups left",
                 "there it is — now nobody's read your world before. that idea is yours."),
                ("omg rewriting everything tonite. tysm",
                 "keep what you love, flip what bores you. that's originality, mostly.")
            ],
            "slots": {
                "book": ["Harry Potter", "Percy Jackson", "Lord of the Rings", "Narnia", "Wings of Fire", "Keeper of the Lost Cities", "Avatar", "The Hobbit", "Eragon", "The Wizard of Earthsea"]
            }
        }
    ]
}
