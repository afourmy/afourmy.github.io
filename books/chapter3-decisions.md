# Chapter 3 decisions

Working file. Write your answer on the `Answer:` line under each question. Anything you leave blank
I will come back and ask about rather than decide myself. Delete this file once the chapter is written.

Your notes map onto Rosalind BA3A to BA3M, so the chapter has no missing algorithms. These
questions are about what to cut, what to add, and how much space a few topics get.

---

## 1. Read length for 2005 sequencing

Your note says next generation sequencing produced reads of "length 20". That looks low to me: the
2005 454 machines gave roughly 100 base pairs, and early Illumina was around 35. I am not going to
silently change your number.

- (a) Keep 20.
- (b) Use "roughly 100" for the 2005 454 machines.
- (c) Say "a few dozen to a few hundred base pairs" and give no single figure.
- (d) Something else.

**Answer:** b

---

## 2. The k value for DNA arrays

You wrote "value of k too small (10?)" with a question mark.

- (a) State $k \approx 10$.
- (b) Say only that $k$ was too small, no figure.

**Answer:** a

---

## 3. How much DNA array history to keep

The 1988 arrays, why they failed (low hybridization fidelity, $k$ too small), and today's use of
arrays for genetic variation.

I recommend (b). The lesson that a small $k$ makes reconstruction fail is worth keeping because it
comes back later with repeats. The rest is history with no algorithm attached to it.

- (a) Keep it in full.
- (b) Compress to two or three sentences, keeping only the "$k$ was too small" lesson.
- (c) Drop the array history entirely.

**Answer:** b

---

## 4. Section order

The choice is where the comparison between Hamiltonian and Eulerian paths goes.

I recommend (a). It makes the comparison the reason to develop Eulerian paths at all, which is the
"this fails because X, so we do Y" chain the prompt asks for. The cost is that "Eulerian is
polynomial" is asserted one section before the algorithm shows it.

- (a) Your notes' order: overlap graph, de Bruijn graph, compare the two, then Euler's theorem and
  the cycle algorithm.
- (b) Overlap graph, de Bruijn graph, Euler's theorem and the algorithm, then compare.

**Answer:** a

---

## 5. Seven Bridges of Königsberg

I recommend (b). The audience already knows Eulerian paths, and the prompt says never explain CS.

- (a) Keep it.
- (b) Drop it.

**Answer:** b

---

## 6. BEST theorem

The number of Eulerian cycles is $c(G) \prod_v (\text{indegree}(v) - 1)!$, where $c(G)$ counts
spanning arborescences.

I recommend (b). Stated in full it needs the Matrix-Tree theorem to justify $c(G)$, which is a real
digression. Used to show the count is huge, it does actual work in the chapter: it is the reason an
Eulerian path does not pin down the genome.

- (a) Full treatment, including what $c(G)$ is and why.
- (b) One paragraph: state the formula, define $c(G)$ in a line, no proof, and use it only to
  establish that many Eulerian paths exist so the genome is not uniquely determined.
- (c) Drop it.

**Answer:** c

---

## 7. De Bruijn's k-universal strings

I recommend (a). It is Rosalind BA3I, and binary strings demonstrate the graph construction more
cheaply than DNA does.

- (a) Keep as a short subsection with code.
- (b) One paragraph, no code, just where the graph's name comes from.
- (c) Drop it.

**Answer:** a

---

## 8. Repeats (not in your notes)

Your notes never say why assembly is hard. Repeated regions are why the graph has many Eulerian
paths, why a small $k$ fails, and why real assembly stops at contigs. Without this the chapter has
no explanation for its own central difficulty. This is the addition I care most about.

- (a) Add a section on repeats.
- (b) Add a paragraph only.
- (c) Leave it out.

**Answer:** a

---

## 9. Read breaking (not in your notes)

You wrote "even after read breaking" but never introduced the idea, so as written that phrase refers
to nothing.

- (a) Add read breaking properly: splitting reads of length $L$ into $k$-mers, and what it buys
  (handles variable read length, and lets $k$ be chosen independently of read length).
- (b) Reword the contigs sentence so it does not mention read breaking.

**Answer:** a

---

## 10. Returning to the four difficulties (not in your notes)

You list four difficulties at the start (DNA is double stranded, some regions have no reads, reads
contain errors, reads have different lengths), then the String Reconstruction Problem assumes all
four away, and the chapter never comes back to them. The prompt requires closing the loop.

- (a) Add a section near the end taking the four difficulties one at a time and saying how each is
  handled or why it is not.
- (b) Cover only the ones that have a real answer in the chapter and say so.
- (c) Leave the difficulties as an opening remark and do not return to them.

**Answer:** a

---

## 11. Read pairs: how much space

Two decisions here.

**Space.**

- (a) Full section: $(k,d)$-mers, paired composition, paired de Bruijn graph. Covers Rosalind BA3J
  and BA3L.
- (b) One paragraph on the idea, no code.
- (c) Drop read pairs.

**Answer:** c

**Framing.** Your note says "transforming read pairs into long virtual reads". That is the naive
approach the book raises in order to reject it, not the method it settles on, which is the paired
de Bruijn graph.

- (a) Present the naive version, show why it fails, then the paired de Bruijn graph.
- (b) Go straight to the paired de Bruijn graph.

**Answer:** b

---

## 12. Contigs

Your notes have contigs as the practical endpoint. Generating them is Rosalind BA3K, and the
mechanism is maximal non-branching paths, BA3M.

- (a) Full section with both: define a contig, then the maximal non-branching path algorithm.
- (b) Define contigs and state the idea without the algorithm.

**Answer:** b

---

## 13. What the chapter closes on

The prompt says a chapter opens on a biological question and ends by answering it. This chapter
opens on sequencing a real genome. The natural ending is contigs from real reads, but I do not know
what application the book uses to close chapter 3 and I am not going to invent one.

- (a) Tell me the case the book uses, and I will use it. Write it here:
- (b) Close on contigs from real sequencing data, stated in general terms with no named organism.
- (c) Something else you have in mind.

**Answer:** I don't know

---

## 14. Anything else

Topics you want in or out that I have not asked about, or anything above where you disagree with my
recommendation.

**Answer:**
