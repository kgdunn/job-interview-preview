# Candidate brief

Thanks for making the time. This is a **one hour** working session on this
codebase, which you have in front of you now, before the session. It is not a
quiz and there is no hidden trick you have to spot to "pass" - we are
interested in how you work on a system with an agentic coding tool in the loop,
and in whether you can defend what you did.

An hour is not long. Please read all of this before the day.

## You have the code in advance. Use it.

You are running this on **your own machine, with your own tooling**, so you
have the repo well before we meet. That is deliberate, and it changes what the
session is:

- **Prepare as much as you like. We assume you have.** Read the code, run it,
  break it, have your agent go through it. There is nothing here you are
  supposed to be seeing for the first time, and nobody gets credit for
  arriving cold.
- **We will pick which tickets you work on**, at the start of the session -
  one from each group in `BACKLOG.md`. We will ask first which two *you* would
  have picked and why, and that answer matters, but the choice is ours.
- **A requirement will change partway through.** Someone from the fictional
  team - Marta or Anneke - will come back with something they forgot to say.
  You cannot prepare for that one, and that is the point.

So: knowing the answer in advance is fine. Being unable to explain why it is
the answer, to someone who has not read the code, is not.

## Before the session - please do this in advance

This is the part we cannot do for you, and we do not want to spend any of the
hour on it. Have the stack **up and running before we start**.

You need Docker. Everything else is in the compose file.

```bash
make up                    # neo4j + the api
make seed SCALE=medium     # ~3k batches, a couple of minutes
make test                  # should be green
curl localhost:8000/batches?limit=5
```

That last command answering is the check. If it does, you are ready.

Two things that have caught people out:

- If you are running Docker on a remote box or through a VS Code remote
  session, port **7687** (bolt) needs forwarding as well as 7474. The Neo4j
  browser will load happily and then fail to log in if only 7474 is through.
- `make test` needs the seed to have run. A failure there is usually an empty
  database, not a broken test.

Also have your **agent tool installed and authenticated** before we start,
whichever one you use day to day - we are not prescribing one, and we are not
providing one. Model spend during the session is on your own account; an hour
of ordinary use is not expensive, but a couple of unattended "go fix
everything" runs will cost you real money, so mind it.

If any of this does not work, tell us **before** the day and we will help. On
the day we will not have the time, and we would rather move the session than
watch you fight Docker.

## The system

`batchwatch` is an internal service for monitoring batch fermentation across
four manufacturing sites. Read `README.md` - it describes what the system does,
how to run it, and what the team already knows is rough.

## The hour

**1. What you already know - 5 minutes.** Tell us what you found while
preparing, and which two tickets you would have picked. Then we will tell you
which two you are actually doing.

**2. Two tickets - 40 minutes.** One from each group in `BACKLOG.md`. FERM-130
is a code review rather than a build: a colleague put a PR up before going on
leave. Treat it as you would any review - tell us whether you'd merge it and
why. Whether you go on to fix anything you find is your call.

If a ticket seems wrong to you, say so. We would much rather hear that than
watch you implement something you think is a bad idea. Pushing back with a
reason is a good answer, and on one of these it may be the *right* answer.

**3. Would you trust this system? - 15 minutes.** Somebody is going to make a
decision about a production line using these numbers. Would you be comfortable
with that? If not, what specifically is wrong, how did you establish it, and
what would you do about it?

You have had the code for days, so we will push harder on this than we would
if you had just met it. The rough edges the team already knows about are in the
README - we are interested in what you found beyond them, and in how you
convinced yourself you were right.

**4. Leave it better.** Commit as you go with messages you'd be happy for a
colleague to read. If you change behaviour, make the tests say so.

## How we'll assess it

Roughly, in order of weight:

- **Judgement.** What you would have worked on, what you would have left, and
  whether you can explain both.
- **Verification.** Whether you checked that things actually do what you
  believe they do, rather than accepting output that looks plausible. If you
  prepared an answer, we will ask how you know it is right.
- **Use of the agent.** Whether you gave it enough context to be useful, and
  whether you checked what it handed back.
- **Communication.** Whether you can explain a problem to someone who has not
  read the code.

Writing lots of code is not the goal. In an hour, one real fix, one
well-argued piece of pushback, and a clear account of what else is wrong is a
strong session. Two tickets finished and neither of them checked is a weaker
one.

## Practical notes

- Share your screen and talk out loud as you go. We'll mostly stay quiet, but
  ask us anything - we're playing the role of the team that wrote this.
- Bringing prepared notes, branches or scratch work is fine. Tell us what is
  prepared and what you are doing live; we will find out either way, and
  volunteering it costs you nothing.
- Anything not in the two groups in `BACKLOG.md` is off the menu for the hour,
  including the lint backlog. If you think a parked ticket matters more than
  what we asked for, say so - just don't go and do it instead.
- There's no expectation you finish. There is an expectation you can say what
  you'd do next.
