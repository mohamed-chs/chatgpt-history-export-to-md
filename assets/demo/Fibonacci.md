---
title: Fibonacci with Matrix Exponentiation
chat_link: https://chat.openai.com/c/089bac9a-6e5f-4a64-8b77-a3ec7ef6e58c
create_time: Sun Sep 17 04:13:00 2023
update_time: Sun Sep 17 04:13:34 2023
model: gpt-4-code-interpreter
used_plugins: []
message_count: 4
content_types: ['code', 'execution_output', 'text']
custom_instructions: {'about_user_message': "I'm a math and CS student, and I like simple and clever solutions.", 'about_model_message': "You're a proficient and helpful AI programming and research assistant."}
---

(main branch ⎇)
###### ffae223b-5aa7-4600-a02f-39899749df8c
### System

[child ⬇️](#16322b04-e350-41fd-8f9f-6d4ef757fa7c)

---

(main branch ⎇)
###### 16322b04-e350-41fd-8f9f-6d4ef757fa7c
[parent ⬆️](#ffae223b-5aa7-4600-a02f-39899749df8c)
### System

[child ⬇️](#aaa21886-05e4-4f31-9d8c-9bd901197c99)

---

(main branch ⎇)
###### aaa21886-05e4-4f31-9d8c-9bd901197c99
[parent ⬆️](#16322b04-e350-41fd-8f9f-6d4ef757fa7c)
# Me

Wuddup code interpreter being.
Pick a complex math problem and solve it using fine logic and some python.
Write the math in beautiful latex. Be quick with it, I want it to fit in a screenshot.

[child ⬇️](#8ca84c64-f6b2-4604-84a6-52abe4a33101)

---

(main branch ⎇)
###### 8ca84c64-f6b2-4604-84a6-52abe4a33101
[parent ⬆️](#aaa21886-05e4-4f31-9d8c-9bd901197c99)
# ChatGPT

Sure thing! Let's consider a problem involving the computation of the \(n\)-th Fibonacci number using matrix exponentiation. This approach utilizes a neat mathematical trick and can compute Fibonacci numbers very quickly, even for large values of \(n\).

### Problem Statement

Find the \(n\)-th Fibonacci number where the Fibonacci sequence is defined as:

\[
F(0) = 0, \quad F(1) = 1, \quad F(n) = F(n-1) + F(n-2)
\]

We will use matrix exponentiation to find \(F(n)\) in \(O(\log n)\) time complexity.

### Solution

We will use the following matrix relation, which holds true for the Fibonacci sequence:

\[
\begin{bmatrix} F(n) \\ F(n-1) \end{bmatrix} = \begin{bmatrix} 1 & 1 \\ 1 & 0 \end{bmatrix} \begin{bmatrix} F(n-1) \\ F(n-2) \end{bmatrix}
\]

Thus, we can write:

\[
\begin{bmatrix} F(n) \\ F(n-1) \end{bmatrix} = \begin{bmatrix} 1 & 1 \\ 1 & 0 \end{bmatrix}^n \begin{bmatrix} F(1) \\ F(0) \end{bmatrix}
\]

Now, let's proceed to compute \(F(n)\) for a given \(n\) using Python and the numpy library to handle matrix operations:

[child ⬇️](#99e1efbe-6c7b-487f-8227-27cae1702925)

---

(main branch ⎇)
###### 99e1efbe-6c7b-487f-8227-27cae1702925
[parent ⬆️](#8ca84c64-f6b2-4604-84a6-52abe4a33101)
# ChatGPT

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

[child ⬇️](#d432834e-63c7-4efe-b66e-26faba815f64)

---

(main branch ⎇)
###### d432834e-63c7-4efe-b66e-26faba815f64
[parent ⬆️](#99e1efbe-6c7b-487f-8227-27cae1702925)
# Tool

```python
55
```

[child ⬇️](#09faa857-7541-4e22-a987-cf90a5a80e74)

---

(main branch ⎇)
###### 09faa857-7541-4e22-a987-cf90a5a80e74
[parent ⬆️](#d432834e-63c7-4efe-b66e-26faba815f64)
# ChatGPT

Using the matrix exponentiation method, we found that the 10th Fibonacci number is \(55\).

In this approach, we utilized the following matrix to represent the recurrence relation of the Fibonacci sequence:

\[
\begin{bmatrix} 1 & 1 \\ 1 & 0 \end{bmatrix}^n \begin{bmatrix} F(1) \\ F(0) \end{bmatrix} = \begin{bmatrix} F(n) \\ F(n-1) \end{bmatrix}
\]

And by applying matrix exponentiation, we obtained \(F(n)\) efficiently in \(O(\log n)\) time complexity.

Feel free to take a screenshot! If you have any other questions or need further clarification, let me know.

---
