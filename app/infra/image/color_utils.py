from __future__ import annotations

import numpy as np


def safe_mean_color(rgb_pixels: np.ndarray, fallback: tuple[int, int, int] = (255, 255, 255)) -> tuple[int, int, int]:
    if rgb_pixels.size == 0:
        return fallback
    mean = rgb_pixels.mean(axis=0)
    return (int(mean[0]), int(mean[1]), int(mean[2]))


def invert_color(color: tuple[int, int, int]) -> tuple[int, int, int]:
    return (255 - color[0], 255 - color[1], 255 - color[2])


def clamp_color(color: tuple[float, float, float]) -> tuple[int, int, int]:
    return tuple(int(max(0, min(255, round(channel)))) for channel in color)


def luminance(color: tuple[int, int, int]) -> float:
    r, g, b = color
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color_a: tuple[int, int, int], color_b: tuple[int, int, int]) -> float:
    lum_a = luminance(color_a) / 255.0
    lum_b = luminance(color_b) / 255.0
    light = max(lum_a, lum_b)
    dark = min(lum_a, lum_b)
    return (light + 0.05) / (dark + 0.05)


def dominant_color(rgb_pixels: np.ndarray, fallback: tuple[int, int, int] = (255, 255, 255)) -> tuple[int, int, int]:
    if rgb_pixels.size == 0:
        return fallback

    flat = rgb_pixels.reshape(-1, 3)
    quantized = (flat // 32).astype(np.int32)
    unique, counts = np.unique(quantized, axis=0, return_counts=True)
    dominant_bucket = unique[counts.argmax()]
    mask = np.all(quantized == dominant_bucket, axis=1)
    return safe_mean_color(flat[mask], fallback=fallback)


def color_distance(rgb_pixels: np.ndarray, color: tuple[int, int, int]) -> np.ndarray:
    if rgb_pixels.size == 0:
        return np.array([], dtype=np.float32)
    flat = rgb_pixels.reshape(-1, 3).astype(np.float32)
    ref = np.array(color, dtype=np.float32)
    return np.linalg.norm(flat - ref, axis=1)
