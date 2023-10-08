# Flame

Simple flame animation algorithm

## Algorithm

The Idea is to have a 2D array of cells that cover the entire screen.
Each cell has a value that represents the intensity of the flame, and the value is in the range of 0 to 256.
These values associated with a palette of color range from black to white, crossing through red, orange and yellow.

![palette.png](https://raw.githubusercontent.com/vitalibo/python-sandbox/assets/flame/docs/palette.png)

The algorithm starts by initializing the bottom row of the array with random values in range of 0 to 255.
Then, for each cell in the array, formula calculates the value:

```
x[i, j] = (x[i - 1, j] + x[i - 2, j] + x[i + 1, j] + x[i + 2, j] + x[i, j - 1] * 5) / 9
```

Finally, the values are mapped to the palette and drawn to the screen.
Applying this algorithm to the entire screen, each frame, results in a flame animation.

![flame.png](https://raw.githubusercontent.com/vitalibo/python-sandbox/assets/flame/docs/flame.gif)
