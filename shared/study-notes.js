(function () {
  const overrides = {
    "046-pilgrim-gait-sheet": {
      idea:
        "A design-usable illustrated gait poster for one grounded three-dot species, built to break the recent manual-and-folio streak by showing several believable stance variants of the same anatomy on a single page.",
      interaction:
        "Pointer movement pushes weight through the nearest walker, widening root stance and shifting head-thread sway. Press or drag to make the bodies brace harder without turning the sheet into a detached control dashboard.",
      next:
        "Push this branch toward a stronger illustration system: more page variants, clearer gait families, and a reusable library of believable limb, bead, and terrain modules that can feed future design work.",
    },
    "045-crimson-sag-weather": {
      idea:
        "A darker generative poster-field built from sagging crimson lanes, calibration ticks, and ember particles, deliberately breaking the recent rooted-organism manual streak and keeping the motion distributed across the whole weather surface.",
      interaction:
        "Pointer movement shears the nearest lanes and thickens the hanging pressure. Click the floating anchors to switch the field law between weighted drop, cross-current braid, and rising flare.",
      next:
        "Push this branch toward a broader graphic language: denser mark families, print-usable layout variants, and a few stateful weather presets that keep it feeling like governed field behavior instead of a generic HUD.",
    },
    "043-kindred-switchfolio": {
      idea:
        "A pale moving switchfolio that keeps the current interface lane but strips it down to a more believable page system: one rooted nonhuman body, side chambers, and manual-like annotations all share the same illustrated surface.",
      interaction:
        "Pointer movement bends the nearest seam, shifts the three-light face, and opens local chambers inside the same page. Click the visible body-law chips to retune brace, weave, or chorus behavior without opening detached controls.",
      next:
        "Push this branch toward a stronger design system: more reusable module types, denser annotation logic, and a few persistent page states that make the folio feel more like a living manual than a single study sheet.",
    },
    "042-signal-spine-manual": {
      idea:
        "A darker printed-interface manual that answers the recent request for a more explicit HTML control surface, using flatter 2D framing and one living segmented spine instead of another detached specimen board or habitat world.",
      interaction:
        "Pointer movement introduces local alignment drift, opens nearby shutters, and bends the traces around the spine. Click the visible protocol control to cycle the page between manual, bias, and flare behaviors.",
      next:
        "Push this branch toward a fuller design system: more typography modules, persistent panel states, and expandable tool cards that keep the page feeling useful without losing the living-body logic.",
    },
    "031-porous-interface-creature": {
      idea:
        "A pale board-creature where the interface and the body are the same object: translucent shell, root-legs, soft probes, and embedded signal anatomy instead of a detached dashboard.",
      interaction:
        "Move the pointer to change gait, connector tension, and inner warmth. Click the mode nodes to switch the board law and make the same anatomy drift, brace, or bloom differently.",
      next:
        "Push it toward a richer embodied interface: clearer emotional states, touch reactions on the body itself, and a more legible mapping between each mode and a visible anatomical consequence.",
    },
    "032-suture-glyph-switchyard": {
      idea:
        "A flatter editorial signal surface built from stitched current lanes, bead relays, and floating grammar cards, so it reads like a living design system instead of another specimen plate.",
      interaction:
        "Move across the board to tug nearby seams and deform the local field. Click the grammar cards to swap the surface logic between stitch, bead, and wake behaviors.",
      next:
        "Develop it into a fuller graphic language: more surface grammars, stronger page-to-page continuity, and semantic inputs that generate new seam patterns instead of only retiming the same board.",
    },
    "033-utterance-fault-weather": {
      idea:
        "A dark relay-weather plate where language becomes structural weather: typed or spoken fragments land as temporary pressure glyphs inside a segmented fault seam.",
      interaction:
        "Type a phrase or use the mic pulse to inject fresh glyphs. Move the pointer to add local shear and turbulence so the same sentence can settle, scar, or flare differently.",
      next:
        "Turn it into a real semantic weather instrument: phrase memory, clearer category-to-visual mapping, and live event inputs from Telegram or SSE instead of only single one-shot injections.",
    },
    "034-bead-root-switchfield": {
      idea:
        "A rooted creature inside a diagonal switchfield, combining design-illustration posture, bead-tendril detail, and embedded signal lanes in one grounded plate.",
      interaction:
        "Pointer movement shifts stance pressure and bends the tendril fan. Click the mode cards to switch brace, bloom, or flare so the same body redistributes weight and field tension in-place.",
      next:
        "Deepen the body logic: better lower-body support, secondary limbs, and more convincing transitions between defensive, open, and overcharged stance states.",
    },
    "035-glyph-limb-folio": {
      idea:
        "A moving editorial anatomy sheet where one rooted alien body behaves like a living illustration folio, with foldable membranes, bead-thread feelers, and distributed inner light.",
      interaction:
        "Move or touch the page to part the nearest flaps and change local membrane tension. Click the sigils to switch the active body law and alter how the poster breathes.",
      next:
        "Expand it into a richer specimen folio: more cutaway layers, cross-sections, and linked annotations so the page can feel like an anatomical system rather than one animated poster plate.",
    },
    "036-crimson-front-console": {
      idea:
        "A true crimson forecast interface built as a usable multi-pane HTML console, where structural weather, relay seams, and pressure cells live inside one page instead of a decorative board.",
      interaction:
        "Use the mode buttons to retune the storm law, drag the sliders to change density, drift, and ember, and move the pointer across the stage to shear the weather map locally.",
      next:
        "Push it toward a stronger product-like fiction: persistent states, event history, semantic presets, and live external signals that make the console feel like it is monitoring something real.",
    },
    "037-triad-pulse-switchboard": {
      idea:
        "A creature-page where a rooted three-node being and its translucent control rail share the same crimson signal surface, so the controls feel bodily rather than detached.",
      interaction:
        "Move the pointer near the plate to thicken local pulse behavior. Click the pulse-law chips to retune orbit spread, tension, and signal pacing inside the same organism.",
      next:
        "Strengthen the triad as a system: asymmetric roles for the three nodes, more visible cross-talk between them, and state transitions that feel like mood synchronization rather than only parameter changes.",
    },
    "038-affection-thread-sanctuary": {
      idea:
        "A small inhabited sanctuary where several rooted beings exchange warmth through thread bridges and hanging membrane canopies, shifting the branch from interface to habitat world.",
      interaction:
        "Move through the scene to bend the local climate and disturb nearby shelters. Click the climate chips to switch the whole sanctuary between different ambient behavioral laws.",
      next:
        "Grow it into a deeper social ecology: more inhabitants, shared events, longer-lived traces of affection or withdrawal, and weather cycles that alter how the creatures approach each other.",
    },
    "039-lucent-relay-folio": {
      idea:
        "A tall translucent conservatory of hanging valves, reflective echoes, and pale signal weather, focused on optical depth and layered observation rather than explicit controls.",
      interaction:
        "Pointer movement shifts the focus plane and sends local wakes through the nearest valves, so the page behaves like a soft inspection field rather than a button-driven console.",
      next:
        "Develop the inspection logic: zoomable regions, stronger refraction states, and more differentiated valve families so the piece can become a serious translucent habitat page.",
    },
    "040-relay-organ-atlas": {
      idea:
        "A darker multi-pane relay atlas that feels close to a usable interface while keeping one grounded bilateral organism as the main carrier of motion and meaning.",
      interaction:
        "Move the pointer over the stage to drive local refraction, asymmetry, and pressure shifts inside the same body. The interaction is embodied: the page answers through the organism rather than a slider farm.",
      next:
        "Carry it toward a real page system: add a few stronger actionable controls, persistent panel states, and event-driven changes so the organism starts behaving like a live instrument instead of a single scene.",
    },
  };

  function slugFromPath(pathname) {
    const match = pathname.match(/\/animations\/([^/]+)\//);
    return match ? match[1] : null;
  }

  function normalizeId(raw) {
    if (!raw) return "";
    return raw.replace(/^#/, "").trim().toLowerCase();
  }

  function inferInteraction(animation) {
    const note = `${animation.notes || ""} ${animation.branch || ""}`.toLowerCase();
    if (/(typed|spoken|text|sentence|phrase|speech|mic)/.test(note)) {
      return "Type or speak into the piece to inject new events, then use pointer motion to shear, stir, or locally redirect the same field.";
    }
    if (/(clicking|click|mode|switch|card|chip|slider|control|console)/.test(note)) {
      return "Move the pointer to disturb the field or body directly, then click the visible cards or controls to retune the same surface instead of opening a detached UI.";
    }
    if (/(habitat|world|valve|membrane|translucent|shoal|reef|canopy|climate)/.test(note)) {
      return "Pointer movement bends nearby membranes, wakes, focus planes, or local climate directly in the world, with no separate control rail needed.";
    }
    if (/(creature|face|paw|body|gaze|mood|emotion|organism)/.test(note)) {
      return "Pointer movement acts on the body itself, changing tension, blush, gait, recoil, or gaze rather than only nudging a background effect.";
    }
    if (/pointer/.test(note)) {
      return "Pointer movement introduces local shear, pressure, and wake behavior inside the same page.";
    }
    return "The piece is mainly atmospheric right now, with lightweight pointer disturbance and no heavy external controls.";
  }

  function inferNext(animation) {
    const note = `${animation.notes || ""} ${animation.branch || ""}`.toLowerCase();
    if (/(typed|spoken|text|sentence|phrase|speech|mic|semantic)/.test(note)) {
      return "Could grow into a stateful semantic instrument with phrase memory, stronger meaning-to-visual mapping, and live event input.";
    }
    if (/(console|control|switchboard|atlas|interface|dashboard|relay)/.test(note)) {
      return "Could grow into a more product-like interface with persistent state, better panel logic, and clearer cause-and-effect between controls and the field.";
    }
    if (/(habitat|world|shoal|reef|garden|sanctuary|climate|canopy)/.test(note)) {
      return "Could grow into a larger habitat page with more inhabitants, slower ecological changes, and longer-lived traces of prior interactions.";
    }
    if (/(creature|face|mood|emotion|paw|organism|body)/.test(note)) {
      return "Could grow into a richer embodied system with more emotional states, touch logic, and clearer anatomical consequences for each mode.";
    }
    if (/(glyph|stencil|diagram|folio|editorial)/.test(note)) {
      return "Could grow into a broader visual grammar with reusable marks, more page states, and stronger continuity across multiple related studies.";
    }
    return "Could grow into a more stateful page with deeper motion logic and a stronger distinction between atmospheric response and real control.";
  }

  function inferIdea(animation) {
    const note = (animation.notes || "").trim();
    if (!note) return "A browser-native motion study in the Creative Taste Bot animation library.";
    return note;
  }

  function describe(animation) {
    const id = normalizeId(animation.id || animation.slug || animation.title);
    const override = overrides[id];
    return {
      idea: override?.idea || inferIdea(animation),
      interaction: override?.interaction || inferInteraction(animation),
      next: override?.next || inferNext(animation),
    };
  }

  function createRow(label, text) {
    const row = document.createElement("div");
    row.className = "study-row";

    const strong = document.createElement("strong");
    strong.className = "study-label";
    strong.textContent = label;

    const p = document.createElement("p");
    p.className = "study-copy";
    p.textContent = text;

    row.appendChild(strong);
    row.appendChild(p);
    return row;
  }

  function ensurePageStyles() {
    if (document.getElementById("study-notes-style")) return;
    const style = document.createElement("style");
    style.id = "study-notes-style";
    style.textContent = `
      .study-annotation {
        width: min(26rem, calc(100vw - 32px));
        border-radius: 24px;
        padding: 16px 18px 18px;
        border: 1px solid rgba(86, 105, 120, 0.18);
        background: rgba(255, 255, 255, 0.68);
        backdrop-filter: blur(18px);
        box-shadow: 0 24px 72px rgba(88, 113, 128, 0.16);
        color: rgba(28, 37, 44, 0.92);
        pointer-events: auto;
        display: grid;
        gap: 10px;
      }
      .study-annotation h2,
      .study-annotation p {
        margin: 0;
      }
      .study-annotation .study-kicker {
        font-size: 11px;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: rgba(34, 56, 71, 0.5);
      }
      .study-annotation h2 {
        font-size: 1rem;
        letter-spacing: -0.02em;
      }
      .study-annotation .study-row {
        display: grid;
        gap: 0.26rem;
      }
      .study-annotation .study-label {
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: rgba(34, 56, 71, 0.56);
      }
      .study-annotation .study-copy {
        font-size: 0.83rem;
        line-height: 1.45;
        color: rgba(34, 56, 71, 0.82);
      }
      @media (max-width: 980px) {
        .study-annotation {
          width: min(100%, 34rem);
        }
      }
    `;
    document.head.appendChild(style);
  }

  function injectPagePanel() {
    const slug = slugFromPath(window.location.pathname);
    if (!slug) return;
    const hud = document.querySelector(".hud");
    if (!hud || document.querySelector(".study-annotation")) return;

    ensurePageStyles();

    const title = document.querySelector("h1")?.textContent?.trim() || slug;
    const note = document.querySelector(".hint")?.textContent?.trim() || "";
    const branch = document.querySelector(".meta")?.textContent?.trim() || "";
    const description = describe({ id: slug, title, notes: note, branch });

    const panel = document.createElement("section");
    panel.className = "study-annotation";
    panel.setAttribute("aria-label", "Study review notes");
    panel.appendChild(Object.assign(document.createElement("p"), { className: "study-kicker", textContent: "Review notes" }));
    panel.appendChild(Object.assign(document.createElement("h2"), { textContent: "Idea, interaction, and what could grow next" }));
    panel.appendChild(createRow("Idea", description.idea));
    panel.appendChild(createRow("Interaction", description.interaction));
    panel.appendChild(createRow("Next", description.next));
    hud.appendChild(panel);
  }

  window.CodeAnimationStudyNotes = {
    describe,
    injectPagePanel,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectPagePanel, { once: true });
  } else {
    injectPagePanel();
  }
})();
