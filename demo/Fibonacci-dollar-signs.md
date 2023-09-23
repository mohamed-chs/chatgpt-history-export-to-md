---
chat_link: "https://chat.openai.com/c/089bac9a-6e5f-4a64-8b77-a3ec7ef6e58c"
title: "Fibonacci with Matrix Exponentiation"
time_created: "17 Sep 2023, 02:13:00"
time_updated: "17 Sep 2023, 02:13:34"
model: "gpt-4-code-interpreter"
total_messages: 3
code_messages: 1
message_types: "execution_output, text, code"
custom_instructions:
  about_user_message: "I'm a math and CS student, and I like simple and clever solutions."
  about_model_message: "You're a proficient and helpful AI programming and research assistant."
---

# Fibonacci with Matrix Exponentiation

# Me
Wuddup code interpreter being.
Pick a complex math problem and solve it using fine logic and some python.
Write the math in beautiful latex. Be quick with it, I want it to fit in a screenshot.

# ChatGPT
Sure thing! Let's consider a problem involving the computation of the $n$-th Fibonacci number using matrix exponentiation. This approach utilizes a neat mathematical trick and can compute Fibonacci numbers very quickly, even for large values of $n$.

### Problem Statement

Find the $n$-th Fibonacci number where the Fibonacci sequence is defined as:

$$
F(0) = 0, \quad F(1) = 1, \quad F(n) = F(n-1) + F(n-2)
$$

We will use matrix exponentiation to find $F(n)$ in $O(\log n)$ time complexity.

### Solution

We will use the following matrix relation, which holds true for the Fibonacci sequence:

$$
\begin{bmatrix} F(n) \\ F(n-1) \end{bmatrix} = \begin{bmatrix} 1 & 1 \\ 1 & 0 \end{bmatrix} \begin{bmatrix} F(n-1) \\ F(n-2) \end{bmatrix}
$$

Thus, we can write:

$$
\begin{bmatrix} F(n) \\ F(n-1) \end{bmatrix} = \begin{bmatrix} 1 & 1 \\ 1 & 0 \end{bmatrix}^n \begin{bmatrix} F(1) \\ F(0) \end{bmatrix}
$$

Now, let's proceed to compute $F(n)$ for a given $n$ using Python and the numpy library to handle matrix operations:

# ChatGPT
### Code Environment :
```python
import numpy as np



# Define the function to find the nth Fibonacci number using matrix exponentiation

def fib_matrix(n):

    F = np.array([[1, 1], [1, 0]], dtype=object)

    return np.linalg.matrix_power(F, n)[0, 1]



# Let's find the 10th Fibonacci number as an example

n = 10

fib_matrix(n)
```

# Code output
### Code Environment :
```python
55
```

# ChatGPT
Using the matrix exponentiation method, we found that the 10th Fibonacci number is $55$.

In this approach, we utilized the following matrix to represent the recurrence relation of the Fibonacci sequence:

$$
\begin{bmatrix} 1 & 1 \\ 1 & 0 \end{bmatrix}^n \begin{bmatrix} F(1) \\ F(0) \end{bmatrix} = \begin{bmatrix} F(n) \\ F(n-1) \end{bmatrix}
$$

And by applying matrix exponentiation, we obtained $F(n)$ efficiently in $O(\log n)$ time complexity.

Feel free to take a screenshot! If you have any other questions or need further clarification, let me know.

