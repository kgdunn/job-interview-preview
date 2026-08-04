# Candidate brief

Thanks for making the time. This is a ~3 hour working session on a real-ish
codebase. It is not a quiz and there is no hidden trick you have to spot to
"pass" - we are interested in how you work on an unfamiliar system with an
agentic coding tool in the loop.

## The setup

`batchwatch` is an internal service for monitoring batch fermentation across
four manufacturing sites. Read `README.md` first - it describes what the system
does, how to run it, and what the team already knows is rough.

You have a box to yourself for the session.

```bash
ssh -i <SSH_KEY_PATH> <SSH_USER>@<EC2_HOST>
cd <REPO_PATH>
```

The repo is already cloned and Docker is installed. The **large** dataset is
already seeded - 4 sites, ~60k batches, several million readings - because
seeding it takes a while. Please don't re-seed at `large` scale unless you mean
to; you'll lose 10+ minutes.

If you want a fast loop, seed the small dataset into a scratch database rather
than blowing away the large one. Ask us and we'll help.

```bash
make up          # bring the stack up
make test        # should be green before you start
curl localhost:8000/batches?limit=5
```

## Your tooling

`<AGENT_TOOL>` is installed and authenticated on the box. Use it as much or as
little as you like - it's there to be used, and we'd rather see you drive it
well than avoid it to prove a point.

**Budget:** you have roughly `<BUDGET_USD>` of model spend for the session.
That is a lot for three hours, but it is not unlimited - a few unattended
"go fix everything" runs against millions of readings will eat it. Keep an eye
on it. If you run out we'll top it up, but we'll ask what happened.

## What we'd like you to do

Work through as much of this as you get to, in whatever order you think is
right. **We do not expect all of it done.** How you choose and sequence is part
of what we're looking at.

1. **Get oriented.** Bring the stack up, poke at the API, and figure out how
   the pieces fit. Ten or fifteen minutes.

2. **Work the backlog.** `BACKLOG.md` has six tickets. Pick them up in the
   order you think is right, and say why. If a ticket seems wrong to you, say
   so - we would much rather hear that than watch you implement something you
   think is a bad idea. Pushing back with a reason is a good answer.

   One of them (FERM-130) is a code review rather than a build: a colleague put
   a PR up before going on leave. Treat it as you would any review - tell us
   whether you'd merge it and why. Whether you go on to fix anything you find
   is your call.

3. **Tell us whether you trust this system.** Somebody is going to make a
   decision about a production line using these numbers. Would you be
   comfortable with that? If not, what specifically is wrong, how did you
   establish it, and what would you do about it? Rough edges the team already
   knows about are in the README; we're interested in anything you find beyond
   that.

4. **Leave it better.** Commit as you go with messages you'd be happy for a
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

Writing lots of code is not the goal. A session that produces one real fix,
one well-argued piece of pushback, and a clear account of what else is wrong is
a strong session.

## Practical notes

- Talk out loud as you go. We'll mostly stay quiet, but ask us anything - we're
  playing the role of the team that wrote this.
- If you get properly stuck on plumbing, say so and we'll unstick you. Fighting
  Docker for forty minutes tells us nothing useful.
- There's no expectation you finish. There is an expectation you can say what
  you'd do next.
