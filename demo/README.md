# PyBryt Demo

To run the demos, first install PyBryt with `pip`:

```
pip install pybryt
```

and then launch the `index.ipynb` notebook in each of the directories under `demo` from Jupyter 
Notebook, which demonstrates the process of using PyBryt to assess student submissions.

## PyBryt is a pedagogical auto assessment library for Python. 


The main goal of PyBryt as compared to other more conventional auto graders is to allow instructors to write more complex assignments that don't require students to follow a rigid structure for their solution.

This allows learners to practice algorithm design, code design and solution implementation while receiving quick and meaningful pedagogical feedback.


## Median Example 

This first example is a somewhat simple one. In it, students are asked to implement a median function, and PyBryt is used to ensure that student solutions correctly implement the algorithm.
In this notebook we have the reference implementation for the median function. A reference implementation is simply a solution that has been marked up with various annotations that assert the presence of different values and conditions on those values.

In this example, we have an implementation of the median algorithm and a series of annotations that assert the presence of a few values. To check that students are computing values that are required to determine the actual value of the median.

In this example, the first value we assert is that students should be sorting the list that they receive into the median function. We then see that they should be determining the length of that list in order to correctly compute the index at which the median lies in the sorted list.

Finally, at the end of the notebook we see an annotation that asserts that the correct value, the value which we know in the test case, should be the median. Is found in memory. All these annotations come with success and failure messages, and these messages will be returned to students when they run PyBryt and also to the instructor when they run PyBryt as a means of providing meaningful feedback to the students.


## Median Demo Submissions 

Note that all the submissions in this demo returned the correct value for the test case and would pass the test of a conventional auto grading solution.

In this example submission, we can see a student has imported NUMPY and returns the value of Np.median called on the input list.

Because the assignment was for students to implement the algorithm themselves, this is not a valid solution, but it does return the correct value. An auto grader wouldn't be able to catch that. This is where PyBryt comes in. If we go and look at the output for this submission, we will see they receive a few messages that let them know that the instructor know that they weren't on the right track and are missing some key values that are needed to satisfy the reference.


## Running PyBryt 

Now let's run PyBryt. The process of running PyBryt is as follows. We first start by compiling a reference implementation, which is the notebook that I showed earlier. After we have compiled the reference information, we can save it to a file if needed, so we cannot reload it later without re executing the notebook or we go straight into grading

## Assessment Process

The process of grading is actually a two stage process.

First, we start by generating a series of memory footprints which are encapsulated in the student implementation objects. To do this, simply executes the notebook or the student submission. With a trace function that records values that it observes in memory. Once we have these memory footprints.

We can then use these and run them against the reference implementations.

To check that they have, we see the right values in memory. Here we can see the results of running PyBryt against the submissions in the demo. If we look at submission 2, which is the one that imported NUMPY we can see a series of error messages that PyBryt was expecting to find certain values that were not included in the student’s submission. In this way we can tell that a student didn't implement the algorithm in good faith, and we know not to give credit to such submissions.


## Fibonacci Demo 

Let's look at a slightly more complex example. This example involves the use of multiple reference implementations.

Here, students are going to be asked to implement a function that returns the NTH Fibonacci number, and which runs in linear time.

In this reference implementation, we have two algorithms for determining the nth Fibonacci number. The first involves the use of a HashMap to remember past values, and the second involves the dynamic programming. We mark up each of these implementations by creating a series of value annotations and appending them to a list. We have two lists, one for the hash implementation and one for the dynamic programming implementation. As we run the test cases in this notebook, we populate these lists with annotations that assert the presence of the HashMap itself in various stages of being filled in for the HashMap implementation and the array of values needed to check the dynamic programming implementation. We also add a second kind of annotation called the time complexity annotation. This is PyBryt mechanism for asserting that a named block of student code runs with a specific runtime.

In this example, we've asserted that it should run in linear time.

Finally, we have a third reference implementation created. In this last reference implementation, will check to see that there are some markers of either of the acceptable implementations in the student’s memory footprint. In this way, we ensure that students are not implementing the naive algorithm, hence the failure message tide to that annotation.

Finally, we create the reference implementation objects by passing the list to the reference implementation constructor along with the name for each reference implementation.


## Fibonacci Demo Submissions

Let's now let’s look at the results of running PyBryt against the submissions.
The three submissions in this submission’s directory includes:

-	A HashMap implementation
-	A dynamic programming implementation
-	A naive implementation.

We can see in these results that the HashMap implementation satisfied the HashMap reference and satisfied the reference concerning that the naive implementation was not being used. We see the dynamic programming satisfied its reference implementation and in the third example, which was the naive example, we see it failed all three references.


## Conclusion 

As you can see, PyBryt allows you to build complex assignments in such a way that students aren't forced to rigidly adhere to a set structure for their submission and is robust in the various failing of comparisons in conventional auto graders.
For more information about PyBryt. You can visit the GitHub repository documentation and see try out the demos.

