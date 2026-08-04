# Candidate brief

Thanks for making the time. This is a **one hour** working session on a
real-ish codebase. It is not a quiz and there is no hidden trick you have to
spot to "pass" - we are interested in how you work on an unfamiliar system with
an agentic coding tool in the loop.

An hour is not long. We have shaped the session so you do not have to spend any
of it on setup or on deciding what to work on.

## The setup

`batchwatch` is an internal service for monitoring batch fermentation across
four manufacturing sites. Read `README.md` first - it describes what the system
does, how to run it, and what the team already knows is rough.

You have a box to yourself, and **the stack is already up and already seeded**
when you arrive: the `medium` dataset, 4 sites, ~3k batches, a few hundred
thousand readings. `make test` was green when we handed it over. You should not
need to build or seed anything.

```bash
ssh -i <SSH_KEY_PATH> <SSH_USER>@<EC2_HOST>
cd <REPO_PATH>
curl localhost:8000/batches?limit=5     # should answer immediately
```

If something is broken when you get there, say so straight away and we will fix
it - that time is ours, not yours. Please don't re-seed unless you mean to;
`make seed SCALE=medium` costs a couple of minutes and `large` costs ten.

## Your tooling

`<AGENT_TOOL>` is installed and authenticated on the box. Use it as much or as
little as you like - it's there to be used, and we'd rather see you drive it
well than avoid it to prove a point.

**Budget:** you have roughly `<BUDGET_USD>` of model spend for the session.
That is plenty for an hour, but it is not unlimited - a couple of unattended
"go fix everything" runs will eat it. If you run out we'll top it up, but we'll
ask what happened.

## What we'd like you to do

Roughly, with the clock:

**1. Get oriented - 5 minutes.** Poke at the API, skim the code, get a picture
of how the pieces fit. Don't try to read all of it.

**2. Two tickets - 40 minutes.** `BACKLOG.md` has four tickets on the menu, in
two groups. **Pick one from each group** and say why you picked the one you
picked.

- Group A: FERM-121 or FERM-130
- Group B: FERM-124 or FERM-127

FERM-130 is a code review rather than a build: a colleague put a PR up before
going on leave. Treat it as you would any review - tell us whether you'd merge
it and why. Whether you go on to fix anything you find is your call.

If a ticket seems wrong to you, say so. We would much rather hear that than
watch you implement something you think is a bad idea. Pushing back with a
reason is a good answer, and on one of these it may be the *right* answer.

**3. Would you trust this system? - 10 minutes.** Somebody is going to make a
decision about a production line using these numbers. Would you be comfortable
with that? If not, what specifically is wrong, how did you establish it, and
what would you do about it? Rough edges the team already knows about are in the
README; we're interested in anything you find beyond that.

We will ask you this directly near the end, so keep a note of anything that
made you uneasy while you were in the code - you don't have to chase it down at
the time.

**4. Leave it better.** Commit as you go with messages you'd be happy for a
colleague to read. If you change behaviour, make the tests say so.

## How we'll assess it

Roughly, in order of weight:

- **Judgement.** What you chose to work on, what you chose to leave, and
  whether you can explain both.
- **Verification.** Whether you checked that things actually do what you
  believe they do, rather than accepting output that looks plausible.
- **Use of the agent.** Whether you gave it enough context to be useful, and
  whether you checked what it handed back.
- **Communication.** Whether you can explain a problem to someone who has not
  read the code.

Writing lots of code is not the goal. In an hour, a session that produces one
real fix, one well-argued piece of pushback, and a clear account of what else
is wrong is a strong session. Two tickets finished and neither of them checked
is a weaker one.

## Practical notes

- Talk out loud as you go. We'll mostly stay quiet, but ask us anything - we're
  playing the role of the team that wrote this.
- If you get properly stuck on plumbing, say so and we'll unstick you. Fighting
  Docker tells us nothing useful and we don't have the hour to spare.
- Anything not on the menu in `BACKLOG.md` is off the menu for today, including
  the lint backlog. If you think one of the parked tickets is more important
  than what we asked for, tell us - just don't go and do it instead.
- There's no expectation you finish. There is an expectation you can say what
  you'd do next.
