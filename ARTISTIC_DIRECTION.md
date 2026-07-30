# Artistic direction: la substantifique moelle

This website is about the beauty in science. Rabelais told his readers to crack the bone and suck out the marrow, la substantifique moelle. That is the standard for every page here: not coverage, not rigor for its own sake, but the marrow. What I truly care about is the beauty in simple things, and the principles that underlie the fabric of reality.

When you write, review, or design anything for this site (a math course, a CS course, physics notes, an algorithm visualization), this is the focus.

## Principles

**1. The goal of a page is the moment something becomes obvious.**
The model of what belongs here is the proof of 1 + 2 + ... + n = n(n+1)/2 by writing the sum forwards and backwards and pairing the terms. Nothing is hidden, nothing is technical, and once you have seen it you cannot unsee it. Every topic should be pushed toward its version of that moment. Prefer the proof that shows *why* over the proof that merely certifies *that*.

**2. Seeing is understanding.**
A drawing is sometimes worth a thousand explanations. Vision is not just another sense alongside hearing or smell: a large share of the brain is devoted to it, and it is our built-in structure detector. When an idea is given visual form (an alignment, a symmetry, a picture), the visual system grasps the structure at a glance, and the idea feels obvious because it is perceived rather than deduced. This works because spatial relations are a faithful model of logical ones: containment maps to implication, adjacency to succession, symmetry to invariance, paths to derivations. A good diagram is therefore a change of encoding in its own right: it replaces a relation the reader would have to check with a relation the eye simply reports. That is exactly what happens in the pairing proof above: the drawing does the reasoning. So for every topic, look for the drawing first. A figure that makes the idea visible beats a paragraph that describes it, and a visualization is not decoration, it is the explanation itself.

**3. The right encoding is the insight.**
Many problems are only hard in the formulation they arrive in. Wavelength allocation becomes graph coloring; DNA assembly becomes an Eulerian path once reads are encoded as a De Bruijn graph. When a subject contains a re-encoding like this, it is the centerpiece of the page, not a remark. Always ask: is there a change of representation under which this problem answers itself?

**4. Frameworks over facts.**
As Bessis describes in Mathematica, strong mathematicians are not people who tolerate more complexity; they are people who have found an easier way to think, a mental picture or technique they reuse across many areas. When a page teaches something, the deliverable is that reusable mental move, stated explicitly. A reader should leave with a way of thinking they can carry elsewhere, not a list of results.

**5. Complexity is never the point.**
Complication can now be delegated to machines; understanding cannot. If a derivation is heavy machinery with no idea inside, compress it to its conclusion or leave it out. Generality, formalism, and edge cases earn their place only when they carry insight. Never decorate complexity; remove it.

**6. Depth means stepping back, not piling up.**
Metamathematics, the philosophy a result uncovers, what it says about how we reason: this is welcome and encouraged. A simple theorem plus an honest reflection on what it reveals is worth more than an advanced theorem stated without understanding.

## Questions to ask of any section

- What is the one idea here? Can I say it in a sentence?
- Can it be *seen* (a picture, an alignment, a symmetry) rather than only computed?
- Is there a re-encoding that makes it trivial?
- What is the reusable mental move, and is it stated explicitly?
- Would the idea survive if all the notation were stripped away? If not, the notation is hiding an absence.

## What to avoid

- Formalism-first exposition, where definitions arrive before the reader knows why they should care.
- Clever tricks that work once and teach nothing.
- Case analysis and machinery presented without the idea that organizes them.
- Completeness as a goal. A page is done when the marrow is exposed, not when the topic is exhausted.
