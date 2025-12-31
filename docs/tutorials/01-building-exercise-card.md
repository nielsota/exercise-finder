# Tutorial: Building an Exercise Card Component

**Goal**: Learn HTML, CSS, and Jinja2 by building a reusable exercise card from scratch.

**What you'll build**: A clean card that displays an exercise with a link to view figures.

**Time**: ~30 minutes

---

## Step 1: Basic HTML Structure

### Theory: Semantic HTML

HTML is about **structure and meaning**, not appearance. We use semantic tags to describe what content *is*, not how it *looks*.

**Key tags:**
- `<article>` - Self-contained content (like a card)
- `<header>` - Top section of content
- `<h3>` - Heading (level 3)
- `<div>` - Generic container (use when no semantic tag fits)
- `<a>` - Link

**Why semantic?**
- Screen readers understand it
- Search engines understand it
- Other developers understand it

### Your Task

Create a new file: `src/exercise_finder/web/templates/_exercise_card_simple.html`

**Write this HTML:**

```html
<article>
  <header>
    <h3>Question 5</h3>
  </header>
  
  <div>
    <p>What is the derivative of f(x) = x² + 3x?</p>
    <a href="/figures/exam-123/q5">View figures</a>
  </div>
</article>
```

**Test it:** Create a test page `test_card.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Exercise Card Test</title>
</head>
<body>
  <article>
    <header>
      <h3>Question 5</h3>
    </header>
    
    <div>
      <p>What is the derivative of f(x) = x² + 3x?</p>
      <a href="/figures/exam-123/q5">View figures</a>
    </div>
  </article>
</body>
</html>
```

**Open in browser**: `open test_card.html`

**Question for you:**
- What do you see? Is it styled?
- Why does it look plain?

<details>
<summary>Answer</summary>

It looks plain because we haven't added CSS yet! HTML is structure only. The browser applies minimal default styling (headings are bold, links are blue, etc).

</details>

---

## Step 2: Adding CSS - The Box Model

### Theory: CSS Box Model

Every HTML element is a **box** with 4 layers:

```
┌─────────────────────────────────┐
│ Margin (outside, transparent)   │
│  ┌───────────────────────────┐  │
│  │ Border                    │  │
│  │  ┌─────────────────────┐  │  │
│  │  │ Padding             │  │  │
│  │  │  ┌───────────────┐  │  │  │
│  │  │  │ Content       │  │  │  │
│  │  │  └───────────────┘  │  │  │
│  │  └─────────────────────┘  │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

**CSS Syntax:**
```css
selector {
  property: value;
}
```

**Common properties:**
- `border` - Line around element
- `padding` - Space inside border
- `margin` - Space outside border
- `border-radius` - Rounded corners
- `background` - Background color

### Your Task

Add a `<style>` section to your `test_card.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Exercise Card Test</title>
  <style>
    /* Step 1: Make the article look like a card */
    article {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 16px;
      max-width: 600px;
      background: white;
    }
    
    /* Step 2: Style the header */
    header {
      padding-bottom: 12px;
      border-bottom: 1px solid #f0f0f0;
      margin-bottom: 12px;
    }
    
    /* Step 3: Remove default margins from h3 */
    h3 {
      margin: 0;
      font-size: 18px;
    }
    
    /* Step 4: Style the link */
    a {
      display: inline-block;
      margin-top: 12px;
      color: #0066cc;
      text-decoration: none;
    }
    
    a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <!-- same HTML as before -->
</body>
</html>
```

**Refresh browser**

**Questions for you:**
1. What does `border-radius: 8px` do?
2. What's the difference between `padding` and `margin`?
3. Why do we set `margin: 0` on `h3`?

<details>
<summary>Answers</summary>

1. `border-radius` rounds the corners. `8px` means 8 pixels of rounding.
2. `padding` is space *inside* the border. `margin` is space *outside* the border.
3. By default, browsers add margin to headings. We remove it for precise control.

</details>

---

## Step 3: CSS Classes for Reusability

### Theory: Why Classes?

**Problem**: The CSS above styles *all* articles on the page.

```css
article { border: 1px solid #e0e0e0; }
```
↑ This affects every `<article>` element!

**Solution**: Use **classes** to target specific elements.

```html
<article class="exercise-card">
```

```css
.exercise-card { border: 1px solid #e0e0e0; }
```
↑ This only affects elements with `class="exercise-card"`

**Naming convention**: Use descriptive, hyphenated names.
- ✅ `.exercise-card`, `.card-header`, `.figure-link`
- ❌ `.card1`, `.blue-box`, `.thing`

### Your Task

Update your HTML to use classes:

```html
<article class="exercise-card">
  <header class="card-header">
    <h3 class="card-title">Question 5</h3>
  </header>
  
  <div class="card-body">
    <p class="card-question">What is the derivative of f(x) = x² + 3x?</p>
    <a class="figure-link" href="/figures/exam-123/q5">View figures →</a>
  </div>
</article>
```

Update your CSS to use classes:

```css
.exercise-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  max-width: 600px;
  background: white;
  margin: 20px;
}

.card-header {
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 12px;
}

.card-title {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.card-body {
  /* Add some spacing */
}

.card-question {
  line-height: 1.6;
  color: #444;
}

.figure-link {
  display: inline-block;
  margin-top: 12px;
  padding: 8px 16px;
  background: #f0f7ff;
  border: 1px solid #cce0ff;
  border-radius: 6px;
  color: #0066cc;
  text-decoration: none;
  font-size: 14px;
}

.figure-link:hover {
  background: #e0efff;
}
```

**Refresh browser**

**Question for you:**
- Try adding another `<article>` without the `exercise-card` class. What happens?
- What does `:hover` mean in CSS?

<details>
<summary>Answers</summary>

- Articles without the class won't be styled. Classes give us control!
- `:hover` is a pseudo-class that applies styles when you mouse over an element.

</details>

---

## Step 4: Making it Dynamic with Jinja2

### Theory: Template Variables

**Problem**: Our HTML is hardcoded. We need dynamic data!

**Jinja2** is a templating language that lets you inject Python data into HTML.

**Basic syntax:**
```jinja2
{{ variable }}           - Print a variable
{% if condition %}       - Conditional
{% for item in list %}   - Loop
```

**Example:**
```python
# Python
exercise = {
    "number": 5,
    "question": "What is 2+2?",
    "exam_id": "exam-123"
}
```

```jinja2
<!-- Template -->
<h3>Question {{ exercise.number }}</h3>
<p>{{ exercise.question }}</p>
```

**Output:**
```html
<h3>Question 5</h3>
<p>What is 2+2?</p>
```

### Your Task

Create `src/exercise_finder/web/templates/exercise_card_test.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Exercise Card Test</title>
  <link rel="stylesheet" href="/static/exercise_card.css">
</head>
<body>
  <article class="exercise-card">
    <header class="card-header">
      <h3 class="card-title">Question {{ exercise.number }}</h3>
    </header>
    
    <div class="card-body">
      <div class="card-question">{{ exercise.question_text }}</div>
      
      {% if exercise.figure_images %}
        <a class="figure-link" href="/figures/{{ exercise.exam_id }}/{{ exercise.number }}">
          View {{ exercise.figure_images|length }} figure(s) →
        </a>
      {% endif %}
    </div>
  </article>
</body>
</html>
```

Move your CSS to `src/exercise_finder/web/static/exercise_card.css` (same CSS as before)

**Test it in your app:**

Add a test route in `src/exercise_finder/web/app/routes.py`:

```python
@router.get("/test-card", response_class=HTMLResponse)
async def test_card(request: Request) -> HTMLResponse:
    """Test the exercise card."""
    exercise = {
        "number": 5,
        "exam_id": "VW-1025-a-19-1-o",
        "question_text": "What is the derivative of f(x) = x² + 3x?",
        "figure_images": ["fig1.png", "fig2.png"]
    }
    return templates.TemplateResponse("exercise_card_test.html", {
        "request": request,
        "exercise": exercise
    })
```

**Visit**: http://localhost:8000/test-card

**Questions for you:**
1. What does `{{ exercise.figure_images|length }}` do?
2. What happens if `figure_images` is empty?
3. How do you access nested data like `exercise.exam_id`?

<details>
<summary>Answers</summary>

1. `|length` is a Jinja2 filter that counts items in a list.
2. If empty, the `{% if %}` block won't render. No link appears.
3. Use dot notation: `{{ exercise.exam_id }}` or brackets: `{{ exercise['exam_id'] }}`

</details>

---

## Step 5: Creating a Reusable Macro

### Theory: Jinja2 Macros

**Macros** are like functions for templates. They let you reuse HTML blocks.

**Syntax:**
```jinja2
{% macro card_name(parameter) %}
  <!-- HTML here -->
  <h3>{{ parameter }}</h3>
{% endmacro %}

<!-- Use it: -->
{{ card_name("Hello") }}
```

**Why macros?**
- ✅ Write once, use many times
- ✅ Consistent styling
- ✅ Easy to update (change one place)

**File organization:**
- Macros go in files starting with `_` (e.g., `_exercise_card.html`)
- Import them where needed

### Your Task

Create `src/exercise_finder/web/templates/_exercise_card.html`:

```jinja2
{# 
  Exercise Card Macro
  
  Usage:
    {% from "_exercise_card.html" import exercise_card %}
    {{ exercise_card(exercise) }}
  
  Parameters:
    - exercise: dict with keys:
      - number: int
      - exam_id: str
      - question_text: str
      - figure_images: list (optional)
#}

{% macro exercise_card(exercise) %}
<article class="exercise-card">
  <header class="card-header">
    <h3 class="card-title">Question {{ exercise.number }}</h3>
  </header>
  
  <div class="card-body">
    <div class="card-question">{{ exercise.question_text }}</div>
    
    {% if exercise.figure_images %}
      <a class="figure-link" href="/figures/{{ exercise.exam_id }}/{{ exercise.number }}">
        View {{ exercise.figure_images|length }} figure(s) →
      </a>
    {% endif %}
  </div>
</article>
{% endmacro %}
```

Now use it in `exercise_card_test.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Exercise Card Test</title>
  <link rel="stylesheet" href="/static/exercise_card.css">
</head>
<body>
  {% from "_exercise_card.html" import exercise_card %}
  
  {{ exercise_card(exercise) }}
</body>
</html>
```

**Test it**: Visit http://localhost:8000/test-card

**Questions for you:**
1. What's the difference between `{# comment #}` and `<!-- comment -->`?
2. How would you display 3 exercise cards on one page?

<details>
<summary>Answers</summary>

1. `{# comment #}` is a Jinja2 comment (not in HTML output). `<!-- comment -->` is an HTML comment (visible in page source).
2. Call the macro 3 times, or use a loop:
   ```jinja2
   {% for ex in exercises %}
     {{ exercise_card(ex) }}
   {% endfor %}
   ```

</details>

---

## Step 6: Using Real Data

### Theory: Connecting Backend to Frontend

**Flow:**
1. Python route fetches data
2. Passes data to template
3. Template renders HTML

**Example:**
```python
@router.get("/exercises")
async def exercises():
    exercises = fetch_from_database()  # Python function
    return templates.TemplateResponse("exercises.html", {
        "request": request,
        "exercises": exercises  # Pass to template
    })
```

### Your Task

Update `src/exercise_finder/web/app/routes.py`:

```python
@router.get("/exercises", response_class=HTMLResponse)
async def exercises(request: Request, authenticated: bool = Depends(require_authentication)) -> HTMLResponse:
    """
    Render the exercises page.
    """
    # TODO: Fetch real exercises from your database/vector store
    # For now, use mock data
    exercises = [
        {
            "number": 1,
            "exam_id": "VW-1025-a-19-1-o",
            "question_text": "Calculate the limit of f(x) = (x²-1)/(x-1) as x→1",
            "figure_images": ["fig1.png"]
        },
        {
            "number": 2,
            "exam_id": "VW-1025-a-19-1-o",
            "question_text": "Find the derivative of g(x) = sin(x) · cos(x)",
            "figure_images": []
        },
        {
            "number": 3,
            "exam_id": "VW-1025-a-19-1-o",
            "question_text": "Solve the integral ∫(2x + 3)dx",
            "figure_images": ["fig1.png", "fig2.png"]
        }
    ]
    
    return templates.TemplateResponse("exercises.html", {
        "request": request,
        "exercises": exercises
    })
```

Update `src/exercise_finder/web/templates/exercises.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Exercises - MathWizard</title>
  <link rel="stylesheet" href="/static/exercise_card.css">
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f9fafb;
      margin: 0;
      padding: 20px;
    }
    
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    
    h1 {
      font-size: 32px;
      margin-bottom: 24px;
      color: #111;
    }
    
    .exercise-list {
      display: grid;
      gap: 16px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Exercises</h1>
    
    <div class="exercise-list">
      {% from "_exercise_card.html" import exercise_card %}
      
      {% for exercise in exercises %}
        {{ exercise_card(exercise) }}
      {% endfor %}
    </div>
  </div>
</body>
</html>
```

**Test it**: Visit http://localhost:8000/exercises

**Final Questions:**
1. How would you add pagination (show 10 exercises per page)?
2. How would you add search/filter functionality?
3. How could you make the figure link open in a modal instead of a new page?

<details>
<summary>Hints</summary>

1. **Pagination**: Add `?page=2` to URL, use `exercises[start:end]` in Python
2. **Search**: Add a form with `<input>` and filter in Python backend
3. **Modal**: Use JavaScript to intercept click, show overlay with figure images

These are great next steps to learn!

</details>

---

## 🎉 Congratulations!

You've built a **reusable exercise card component** and learned:

✅ HTML structure with semantic tags  
✅ CSS box model and styling  
✅ CSS classes for reusability  
✅ Jinja2 variables and conditionals  
✅ Jinja2 macros for components  
✅ Connecting backend Python to frontend templates  

## Next Steps

**Level up your skills:**
1. 📚 [MDN HTML Tutorial](https://developer.mozilla.org/en-US/docs/Learn/HTML)
2. 🎨 [CSS Tricks Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
3. 🔧 [Jinja2 Documentation](https://jinja.palletsprojects.com/)

**Enhance your exercise card:**
- Add difficulty badges
- Add bookmark/favorite functionality
- Add answer reveal (requires JavaScript)
- Add tags/categories
- Add time estimates

**Practice challenge:**
Build a similar component for:
- Solution explanations
- User progress dashboard
- Exam summary cards

Keep building! 🚀

