<  n me="re dme-top"></ >

# M3D — Oper tion l Intelligence R ntime

**An open-so rce r ntime  or s  e,   tonomo s AI oper tions.**

[![License](https://img.shields.io/gith b/license/M3DMedi /M3D?style= l t-sq  re)](https://gith b.com/M3DMedi /M3D/blob/m in/LICENSE)
[![Python](https://img.shields.io/b dge/Python-3.13% B-3  6AB?style= l t-sq  re&logo=python&logoColor=white)](https://www.python.org/)
[![GitH b St rs](https://img.shields.io/gith b/st rs/M3DMedi /M3D?style= l t-sq  re&logo=gith b)](https://gith b.com/M3DMedi /M3D/st rg zers)
[![GitH b Iss es](https://img.shields.io/gith b/iss es/M3DMedi /M3D?style= l t-sq  re)](https://gith b.com/M3DMedi /M3D/iss es)

[Q ick St rt](#q ick-st rt) · [Architect re](# rchitect re) · [S  ety Model](#s  ety-model) · [Ro dm p](#ro dm p) · [Contrib ting](#contrib ting)

---

## C rrent St t s

> **M3D v1. .  — Fo nd tion l Rele se**
>
> The initi l rele se est blishes the oper tion l dom in model, s  ety  rchitect re, environment  bstr ction, orchestr tion, CLI,  nd re l-environment testing.

M3D is  n open-so rce Python r ntime  or b ilding oper tion l intelligence systems th t c n observe re l environments, investig te problems, re son  bo t possible c  ses,  pply policy  nd risk controls, exec te   thorized  ctions, veri y o tcomes,  nd m int in  n   dit ble oper tion l history.

M3D is designed to sit between **AI re soning  nd re l-world oper tions**.

> **AI m y re son  bo t the environment, b t M3D owns oper tion l tr th, policy, exec tion, veri ic tion,  nd   dit bility.**

```merm id
 lowch rt TD
    AI[AI Re soning] --> OBS[Observe]
    OBS --> INV[Investig te]
    INV --> REA[Re son]
    REA --> RISK[Assess Risk]
    RISK --> POL[Apply Policy]
    POL --> AUTH[A thorize]
    AUTH --> ACT[Act]
    ACT --> VER[Veri y]
    VER --> AUD[A dit]
    AUD --> ENV[Oper tion l Environment]
```

---

## Why M3D?

AI systems  re becoming incre singly c p ble o  re soning, pl nning,  nd  sing tools.

The di  ic lt p rt is wh t h ppens when  n AI system inter cts with   re l environment.

An oper tion l system needs to know:

- Wh t exists?
- Wh t ch nged?
- Wh t is    ected?
- Wh t evidence s pports   concl sion?
- Wh t co ld be c  sing the problem?
- Wh t  ctions  re permitted?
- Wh t risks  re involved?
- Who   thorized  n  ction?
- Wh t  ct  lly h ppened?
- Did the  ction  chieve its intended res lt?
- Wh t sho ld be recorded  or   t re investig tion?

M3D provides   str ct red r ntime  or  nswering these q estions.

Its core principle is:

> **AI m y re son  bo t the environment, b t M3D owns oper tion l tr th, policy, exec tion, veri ic tion,  nd   dit bility.**

---

## Wh t M3D Is

M3D is designed to sit between **AI re soning  nd re l-world oper tions**.

The go l is not to b ild  nother ch tbot, generic  gent  r mework, monitoring d shbo rd, or in r str ct re   tom tion tool.

The go l is to provide the **oper tion l  o nd tion th t  llows intelligent systems to s  ely  nderst nd  nd  ct on re l environments.**

M3D provides re s ble primitives  or:

- 🔍 Str ct red oper tion l investig tion
- 🧠 Evidence-b sed re soning
- 🛡️ Policy en orcement
- ⚠️ Risk  ssessment
- 🔐 Explicit   thoriz tion
- ⚙️ Controlled exec tion
- ✅ O tcome veri ic tion
- 📜 Oper tion l   dit bility
- 🔌 Extensible environment integr tions
- 🧪 Testing  nd ev l  tion

---

## Wh t M kes M3D Di  erent?

M3D tre ts oper tions  s   str ct red li ecycle r ther th n   seq ence o  AI tool c lls.

```merm id
 lowch rt LR
    OBS[Observe] --> UNDER[Underst nd]
    UNDER --> INV[Investig te]
    INV --> REASON[Re son]
    REASON --> RISK[Assess Risk]
    RISK --> POLICY[Apply Policy]
    POLICY --> AUTH[A thorize]
    AUTH --> ACT[Act]
    ACT --> VERIFY[Veri y]
    VERIFY --> AUDIT[A dit]
    AUDIT --> LEARN[Le rn]
```

E ch st ge is represented by explicit dom in objects  nd controlled thro gh dedic ted engines  nd inter  ces.

This cre tes   sep r tion between:

| Responsibility | M3D |
|---|---|
| AI re soning | Intelligence |
| Oper tion l st te | So rce o  tr th |
| Evidence | Proven nce |
| Investig tion | Str ct red re soning process |
| Policy | A thority |
| Risk | Conseq ence  ssessment |
| A thoriz tion | Permission |
| Action | Exec tion intent |
| Action Res lt | Exec tion o tcome |
| Veri ic tion | Proo  |
| A dit | Acco nt bility |

This sep r tion is   nd ment l to the  rchitect re.

---

# Core Concepts

M3D models oper tion l environments  sing explicit dom in concepts.

### Environment

An oper tion l bo nd ry s ch  s:

- Lin x server
- m cOS workst tion
- Windows system
- VMw re in r str ct re
- Docker environment
- K bernetes cl ster
- D t b se
- Clo d environment
- Network
- AI  gent
- Web  pplic tion

### Entity

An object inside  n environment.

Ex mples:

- Host
- VM
- Process
- Cont iner
- Service
- D t b se
- User
- AI  gent

### Rel tionship

A  irst-cl ss rel tionship between entities.

Ex mples:

~~~text
HOSTS
DEPENDS_ON
RUNS_ON
CONNECTS_TO
~~~

### Event

An imm t ble   ct describing something th t h ppened or ch nged.

Events cont in in orm tion s ch  s:

- timest mp
- so rce
- entity
- event type
- previo s st te
- new st te
- severity
- met d t 
- correl tion ID

### Investig tion

A str ct red process  or  nderst nding  n oper tion l sit  tion.

```merm id
st teDi gr m-v 
    [*] --> CREATED
    CREATED --> SCOPING
    SCOPING --> COLLECTING
    COLLECTING --> ANALYZING
    ANALYZING --> HYPOTHESIS
    HYPOTHESIS --> TESTING
    TESTING --> HYPOTHESIS
    TESTING --> CONCLUSION
    CONCLUSION --> COMPLETED
    TESTING --> REJECTED
    HYPOTHESIS --> CANCELLED
```

### Evidence

In orm tion s pporting or we kening   hypothesis.

Evidence m int ins proven nce so th t concl sions c n be tr ced b ck to observ tions.

### Hypothesis

A possible expl n tion  or  n observed sit  tion.

```merm id
st teDi gr m-v 
    [*] --> PROPOSED
    PROPOSED --> TESTING
    TESTING --> SUPPORTED
    TESTING --> WEAKENED
    TESTING --> REJECTED
    SUPPORTED --> CONFIRMED
```

A s pported hypothesis is not   tom tic lly con irmed. Con irm tion req ires s   icient evidence.

### Decision

A determin tion o  wh t sho ld h ppen.

A decision is sep r te  rom the re soning th t prod ced it  nd  rom the  ction th t m y event  lly implement it.

### Risk

An independent  ssessment o  potenti l conseq ences.

Risk considers   ctors s ch  s:

- severity
- prob bility
- imp ct
- reversibility
-    ected entities
- mitig tion
- req ired   thoriz tion

### Policy

R les governing wh t the system is  llowed to do.

Policies c n:

~~~text
ALLOW
DENY
REQUIRE_APPROVAL
~~~

AI re soning c nnot override policy.

### Policy Ev l  tion

The res lt o  ev l  ting  n  ction or decision  g inst  pplic ble policy.

```merm id
st teDi gr m-v 
    [*] --> PENDING
    PENDING --> EVALUATED
    EVALUATED --> ALLOWED
    EVALUATED --> DENIED
    EVALUATED --> REQUIRES_APPROVAL
```

Policy ev l  tion is deliber tely sep r ted  rom policy de inition.

### A thoriz tion

Permission to per orm  n oper tion l  ction.

A thoriz tion is deliber tely sep r te  rom the decision itsel .

```merm id
st teDi gr m-v 
    [*] --> REQUESTED
    REQUESTED --> GRANTED
    REQUESTED --> DENIED
    REQUESTED --> EXPIRED
```

### Action

An intended oper tion l oper tion.

```merm id
st teDi gr m-v 
    [*] --> PROPOSED
    PROPOSED --> AUTHORIZED
    AUTHORIZED --> EXECUTING
    EXECUTING --> COMPLETED
    EXECUTING --> FAILED
    PROPOSED --> REJECTED
    PROPOSED --> CANCELLED
    COMPLETED --> ROLLED_BACK
```

### Action Res lt

The observed res lt o  exec ting  n  ction.

Exec tion s ccess is not   tom tic lly considered oper tion l s ccess.

### Veri ic tion

Veri ic tion determines whether the intended o tcome  ct  lly occ rred.

```merm id
st teDi gr m-v 
    [*] --> PENDING
    PENDING --> IN_PROGRESS
    IN_PROGRESS --> VERIFIED
    IN_PROGRESS --> FAILED
    IN_PROGRESS --> INCONCLUSIVE
```

### A dit

M3D m int ins  n imm t ble oper tion l history.

The   dit l yer records wh t h ppened, who or wh t initi ted it, why it h ppened,  nd how the oper tion progressed.

---

# Architect re

M3D  ses   ports- nd- d pters  rchitect re th t keeps the oper tion l core independent  rom in r str ct re, stor ge,  nd AI providers.

The  rchitect re is b ilt  ro nd   strict sep r tion o  responsibilities:

- **Dom in** de ines oper tion l tr th  nd st te.
- **Ports** de ine contr cts between the core  nd extern l c p bilities.
- **Engines** implement investig tion, policy, risk,  ction, veri ic tion,  nd   dit beh vior.
- **Ad pters** connect those contr cts to re l environments, stor ge systems, event b ses,  nd re soning providers.
- **Orchestr tion** coordin tes complete oper tion l work lows.
- **Inter  ces** expose M3D to  sers  nd extern l systems.

```merm id
 lowch rt TB
    INTERFACES[Inter  ces] --> ORCH[Orchestr tion]
    ORCH --> INVEST[Investig tion Engine]
    ORCH --> POLICY[Policy Engine]
    ORCH --> RISK[Risk Engine]
    ORCH --> ACTION[Action Engine]
    ORCH --> VERIFY[Veri ic tion Engine]
    ORCH --> AUDIT[A dit Engine]
    INVEST --> PORTS[Ports]
    POLICY --> PORTS
    RISK --> PORTS
    ACTION --> PORTS
    VERIFY --> PORTS
    AUDIT --> PORTS
    PORTS --> ADAPTERS[Ad pters]
    ADAPTERS --> ENV[Environments]
    ADAPTERS --> STORAGE[Stor ge]
    ADAPTERS --> EVENTS[Event B s]
    ADAPTERS --> AI[Re soning Providers]
    DOMAIN[Dom in] --> INVEST
    DOMAIN --> POLICY
    DOMAIN --> RISK
    DOMAIN --> ACTION
    DOMAIN --> VERIFY
    DOMAIN --> AUDIT
```

The import nt bo nd ry is between the **M3D core**  nd its  d pters.

The dom in does not know whether  n oper tion t rgets Lin x, m cOS, Windows, VMw re, Docker, K bernetes,   d t b se, or   clo d environment. It works with st ble dom in models  nd explicit port contr cts.

Environment integr tions  re implemented  s  d pters:

```merm id
 lowch rt LR
    PORTS[Environment Ports]
    PORTS --> LINUX[Lin x]
    PORTS --> MACOS[m cOS]
    PORTS --> WINDOWS[Windows]
    PORTS --> VMWARE[VMw re]
    PORTS --> DOCKER[Docker]
    PORTS --> K8S[K bernetes]
    PORTS --> CLOUD[Clo d]
    PORTS --> DB[D t b ses]
```

The s me principle  pplies to other repl ce ble c p bilities:

```merm id
 lowch rt LR
    CORE[M3D Core]
    CORE --> STORAGE[Stor ge Ad pters]
    CORE --> EVENTS[Event B s Ad pters]
    CORE --> REASONING[Re soning Ad pters]
    CORE --> ENV[Environment Ad pters]
    STORAGE --> SQLITE[SQLite]
    EVENTS --> MEMORY[In-Memory]
    REASONING --> PROVIDERS[AI / Loc l Models]
    ENV --> SYSTEMS[Oper tion l Environments]
```

This  llows in r str ct re  nd AI providers to evolve witho t  orcing provider-speci ic concerns into the oper tion l dom in.

---

## Architect r l L yers

```merm id
 lowch rt TB
    DOMAIN[Dom in] --> PORTS[Ports]
    PORTS --> ENGINES[Engines]
    ORCHESTRATION[Orchestr tion] --> ENGINES
    INTERFACES[Inter  ces] --> ORCHESTRATION
    ADAPTERS[Ad pters] --> PORTS
```

### Dom in

The dom in cont ins the oper tion l model: environments, entities, events, investig tions, evidence, hypotheses, decisions, risk, policy,   thoriz tion,  ctions, res lts, veri ic tion,  nd   dit records.

### Ports

Ports de ine contr cts  or c p bilities s ch  s environment  ccess, stor ge, re soning, event p blic tion,   thoriz tion, exec tion, veri ic tion,  nd   dit.

### Engines

Engines implement oper tion l beh vior while rem ining independent o  concrete in r str ct re.

### Ad pters

Ad pters implement ports  or speci ic environments  nd technologies.

### Orchestr tion

Orchestr tion coordin tes complete oper tion l  lows  cross the engines. It does not repl ce the dom in or the engines.

### Inter  ces

Inter  ces expose M3D c p bilities to  sers  nd extern l systems, incl ding the comm nd-line inter  ce.

This str ct re keeps the core test ble, repl ce ble,  nd extensible while  llowing new environments, providers,  nd inter  ces to be  dded independently.

---

# AI Is Not the So rce o  Tr th

M3D deliber tely sep r tes intelligence  rom oper tion l   thority.

```merm id
 lowch rt TB
    AI[AI Re soning] --> CORE[M3D Core]
    CORE --> STATE[Oper tion l St te]
    CORE --> EVIDENCE[Evidence]
    CORE --> INVESTIGATION[Investig tion]
    CORE --> POLICY[Policy]
    CORE --> RISK[Risk]
    CORE --> AUTH[A thoriz tion]
    CORE --> EXECUTION[Exec tion]
    CORE --> VERIFICATION[Veri ic tion]
    CORE --> AUDIT[A dit]
```

AI re soning providers c n be repl ced witho t ch nging the oper tion l model.

Potenti l providers incl de:

- OpenAI
- Anthropic
- Loc l models
- F t re re soning systems

The AI l yer c n propose hypotheses, investig tion steps, concl sions,  nd decisions.

The M3D core rem ins responsible  or oper tion l st te, evidence, policy,   thoriz tion, exec tion, veri ic tion,  nd   dit.

# S  ety Model

M3D is designed  ro nd controlled   tonomy.

An intelligent system sho ld not simply:

~~~text
AI → Tool → Comm nd
~~~

Inste d:

```merm id
 lowch rt LR
    THINK[Think] --> ASSESS[Assess]
    ASSESS --> POLICY[Policy]
    POLICY --> RISK[Risk]
    RISK --> AUTH[A thoriz tion]
    AUTH --> EXECUTE[Exec te]
    EXECUTE --> VERIFY[Veri y]
    VERIFY --> AUDIT[A dit]
```

This  llows systems to oper te with di  erent   tonomy levels.

### Observ tion Only

The system c n inspect environments  nd collect in orm tion.

### Investig tion

The system c n investig te oper tion l sit  tions  nd develop hypotheses.

### Recommend tion

The system c n propose  ctions witho t exec ting them.

### Approv l-B sed Oper tions

The system c n exec te  ctions   ter explicit   thoriz tion.

### Controlled A tonomy

The system c n exec te pre-  thorized cl sses o  low-risk  ctions while m int ining veri ic tion  nd   dit bility.

The r ntime is designed so th t incre sing   tonomy does not req ire removing the s  ety model.

---

# Environment Abstr ction

M3D environments expose str ct red c p bilities thro gh environment pl gins.

Concept  lly:

~~~text
identi y()
discover()
observe()
collect()
exec te()
veri y()
~~~

This m kes it possible to  se the s me oper tion l model  cross di  erent environments.

The initi l implement tion incl des:

- m cOS environment s pport
- Lin x environment s pport
- environment discovery
- environment observ tion
- environment d t  collection
- controlled exec tion inter  ces
- o tcome veri ic tion

Addition l  d pters c n be  dded witho t ch nging the core oper tion l model.

---

# M3D v1. . 

The initi l rele se est blishes the  o nd tion l oper tion l model.

C rrent c p bilities incl de:

- imm t ble oper tion l dom in models
- environments
- entities
- rel tionships
- events
- investig tions
- evidence
- hypotheses
- decisions
- risk  ssessment
- policies
- policy ev l  tion
-   thoriz tion
-  ctions
-  ction res lts
- veri ic tion
-   dit records
- investig tion persistence inter  ces
- event b s inter  ces
- environment pl gin inter  ces
- re soning inter  ces
- policy engine
- risk engine
-  ction engine
- veri ic tion engine
-   dit engine
- oper tion l orchestr tion
- m cOS environment integr tion
- Lin x environment integr tion
- comm nd-line inter  ce
-  nit testing
- integr tion testing
- re l-environment m cOS testing

The project is intention lly  o nd tion l  t this st ge.

M3D v1. .  is **not positioned  s   prod ction   tonomo s IT oper tions pl t orm yet**.

It est blishes the  rchitect re  nd primitives req ired to b ild one.

---

# Q ick St rt

A ter inst ll tion, inspect yo r loc l environment:

~~~b sh
m3d env in o
~~~

Discover the entities M3D c n c rrently see:

~~~b sh
m3d env list
~~~

Observe the l test environment events:

~~~b sh
m3d env events
~~~

Collect det iled host in orm tion:

~~~b sh
m3d env get host
~~~

A typic l  low looks like:

~~~text
$ m3d env in o
Environment: m cos_loc l

$ m3d env list
HOST
  id: entity_...
  n me: yo r-host
  st t s: online
~~~

This is intention lly sm ll in v1:

**connect → observe → inspect**

The s me environment  bstr ction will l ter s pport investig tion, policy-controlled  ctions, veri ic tion,  nd   tonomo s oper tion l work lows.

---

# Comm nd Line Inter  ce

M3D c rrently provides   lightweight CLI.

~~~b sh
m3d --help
~~~

Displ y the  v il ble comm nds.

~~~b sh
m3d env in o
~~~

Displ y in orm tion  bo t the connected environment.

~~~b sh
m3d env list
~~~

List discovered entities.

~~~b sh
m3d env events
~~~

Displ y observed events.

~~~b sh
m3d env get host
~~~

Collect det iled in orm tion  bo t the host.

The CLI will evolve  longside the r ntime.

---

# Inst ll tion

Clone the repository:

~~~b sh
git clone https://gith b.com/M3DMedi /M3D.git
cd M3D
~~~

Cre te   Python environment:

~~~b sh
cond  cre te -n m3d python=3.13
cond   ctiv te m3d
~~~

Inst ll M3D in edit ble mode:

~~~b sh
pip inst ll -e .
~~~

Inst ll development dependencies:

~~~b sh
pip inst ll -e ".[dev]"
~~~

R n the test s ite:

~~~b sh
pytest
~~~

---

# Development

M3D c rrently t rgets Python 3.13+.

Development tooling incl des:

- pytest
- pytest-cov
- R   
- mypy

Code q  lity c n be checked with:

~~~b sh
r    check .
~~~

Type checking c n be per ormed with:

~~~b sh
mypy src
~~~

Tests c n be exec ted with:

~~~b sh
pytest
~~~

The project is intended to m int in strict sep r tion between dom in logic, inter  ces, engines,  nd in r str ct re  d pters.

---

# Testing

M3D is being developed with testing  s p rt o  the  rchitect re r ther th n  s    in l v lid tion step.

The test s ite covers:

~~~text
tests/
├──  nit/
├── integr tion/
├── scen rios/
└── benchm rks/
~~~

The v1 development b seline incl des h ndreds o    tom ted tests covering the dom in model, engines, ports,  d pters, orchestr tion,  nd re l m cOS integr tion.

Re l-environment testing is especi lly import nt bec  se oper tion l so tw re m st be v lid ted  g inst  ct  l systems r ther th n only mocked environments.

---

# Project Str ct re

~~~text
M3D/
├── src/m3d/
│   ├── dom in/
│   │   ├── environment/
│   │   ├── entity/
│   │   ├── rel tionship/
│   │   ├── event/
│   │   ├── investig tion/
│   │   ├── evidence/
│   │   ├── hypothesis/
│   │   ├── decision/
│   │   ├── risk/
│   │   ├── policy/
│   │   ├── policy_ev l  tion/
│   │   ├──   thoriz tion/
│   │   ├──  ction/
│   │   ├──  ction_res lt/
│   │   ├── veri ic tion/
│   │   ├──   dit/
│   │   └── common/
│   │
│   ├── ports/
│   ├── engines/
│   ├──  d pters/
│   ├── r ntime/
│   └── inter  ces/
│       └── cli/
│
├── tests/
│   ├──  nit/
│   ├── integr tion/
│   ├── scen rios/
│   └── benchm rks/
│
├── ex mples/
├── docs/
├── benchm rks/
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
└── .gitignore
~~~

---

# Who Is M3D For?

M3D is intended  or people b ilding systems th t need to re son  bo t  nd oper te re l environments.

### Developers

B ilding AI-powered oper tion l systems witho t h ving to reinvent:

- st te m n gement
- investig tion models
- policy en orcement
-   thoriz tion
- exec tion
- veri ic tion
-   dit bility

### AI Engineers

B ilding  gents th t need to inter ct with re l in r str ct re while m int ining explicit oper tion l controls.

### Pl t orm  nd In r str ct re Te ms

Cre ting   tom tion  nd oper tion l intelligence systems  cross heterogeneo s environments.

### Sec rity Te ms

B ilding systems where  ctions req ire explicit policy,   thoriz tion, veri ic tion,  nd   dit tr ils.

### Comp nies

Using M3D  s  n open  o nd tion  or intern l oper tion l intelligence systems or commerci l prod cts.

### Rese rchers

Experimenting with:

-   tonomo s oper tions
- AI re soning
-  gent s  ety
- oper tion l decision m king
- veri ic tion
- h m n-in-the-loop systems
- AI ev l  tion

---

# Ro dm p

The project is expected to evolve thro gh sever l st ges.

## v1 — Fo nd tion

Est blish the oper tion l model  nd core  rchitect re.

~~~text
Dom in
Ports
Engines
Ad pters
Orchestr tion
CLI
Testing
~~~

## v1.x — R ntime

Introd ce the r ntime l yer th t connects the  o nd tion l components into   coherent oper tion l exec tion environment.

Potenti l  re s incl de:

- event-driven orchestr tion
- persistent r ntime st te
- sched ling
- oper tion l work lows
- richer environment discovery
- pl gin m n gement
- r ntime con ig r tion

## v  — A tonomo s Oper tions

Exp nd the re soning  nd oper tion l c p bilities.

Potenti l  re s incl de:

-  dv nced investig tions
- m lti-step oper tions
-   tonomo s remedi tion
- m lti- gent coordin tion
- oper tion l memory
- richer veri ic tion
- sim l tion environments
- policy-driven   tonomy

## F t re

The long-term direction is  n ecosystem  ro nd oper tion l intelligence.

Potenti l components incl de:

~~~text
M3D Core
    │
    ├── Environment Pl gins
    ├── Re soning Providers
    ├── Policy P cks
    ├── Oper tion l Pl ybooks
    ├── Veri ic tion Mod les
    ├── Benchm rks
    ├── Integr tions
    └── Comm nity Knowledge
~~~

---

# Contrib ting

M3D is intended to become   comm nity-driven project.

Contrib tions  re welcome  cross:

- Python development
- environment  d pters
- AI re soning integr tions
- policy systems
- veri ic tion
- testing
- benchm rks
- doc ment tion
- sec rity
- oper tion l rese rch
- ex mples  nd  se c ses

The project is especi lly interested in contrib tors who w nt to explore the bo nd ry between **AI re soning  nd s  e re l-world  ction**.

See `CONTRIBUTING.md`  or development g idelines.

---

# Design Principles

M3D is b ilt  ro nd sever l principles.

### 1. AI sho ld not own oper tion l tr th

Models c n re son  bo t st te, b t the r ntime m int ins the   thorit tive oper tion l model.

###  . Actions m st be controlled

Exec tion sho ld p ss thro gh policy, risk,   thoriz tion,  nd veri ic tion.

### 3. Evidence m tters

Concl sions sho ld be tr ce ble to observ tions  nd evidence.

### 4. Veri ic tion is p rt o  the oper tion

A s ccess  l comm nd is not necess rily   s ccess  l oper tion.

### 5. A dit bility is p rt o  the  rchitect re

Oper tion l history sho ld not be  n   tertho ght.

### 6. Environments sho ld be repl ce ble

The core sho ld not be co pled to   speci ic in r str ct re provider.

###  . A tonomy sho ld be controll ble

The system sho ld s pport h m n oversight  nd progressively incre sing levels o    tonomy.

### 8. The  rchitect re sho ld rem in extensible

New environments, AI providers, policies, veri ic tion methods,  nd oper tion l c p bilities sho ld be  dd ble witho t rewriting the core.

---

# Comm nity

M3D is  n open-so rce project  nd welcomes:

- ⭐ St rs  nd  ollows
- 🐛 B g reports
- 💡 Fe t re propos ls
- 🔌 Pl gin contrib tions
- 🧪 Experiments  nd benchm rks
- 🔧 P ll req ests
- 💬 Architect re disc ssions

Use  l st rting points:

- [Repository](https://gith b.com/M3DMedi /M3D)
- [Iss es](https://gith b.com/M3DMedi /M3D/iss es)
- [Disc ssions](https://gith b.com/M3DMedi /M3D/disc ssions)

I  M3D is  se  l to yo ,   GitH b st r helps other developers discover the project.

---

# Sec rity

Oper tion l so tw re req ires   strong sec rity model.

Sec rity iss es sho ld be reported responsibly r ther th n disclosed p blicly  s ordin ry GitH b iss es.

See `SECURITY.md`  or the project sec rity policy.

---

# License

M3D is rele sed  nder the **Ap che License  . **.

See `LICENSE`  or the complete license text.

---

# The Vision

The   t re o  AI oper tions sho ld not be:

~~~text
AI → Tool → Comm nd
~~~

It sho ld be:

```merm id
 lowch rt TB
    ENV[Environment] --> OBS[Observ tion]
    OBS --> UNDER[Underst nding]
    UNDER --> INV[Investig tion]
    INV --> REASON[Re soning]
    REASON --> RISK[Risk]
    RISK --> POLICY[Policy]
    POLICY --> AUTH[A thoriz tion]
    AUTH --> ACTION[Action]
    ACTION --> VERIFY[Veri ic tion]
    VERIFY --> AUDIT[A dit]
    AUDIT --> LEARN[Oper tion l Le rning]
```

M3D is being b ilt to provide the r ntime  nderne th th t model.

The long-term go l is  n open ecosystem where developers, comp nies, rese rchers,  nd in r str ct re te ms c n b ild incre singly c p ble oper tion l intelligence systems on top o    common,   dit ble  o nd tion.

**M3D — Oper tion l Intelligence R ntime.**
