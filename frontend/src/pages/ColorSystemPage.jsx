import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const colorScales = [
  {
    name: 'Brand',
    prefix: 'brand',
    description: 'Primary brand identity — Big Mann Entertainment signature purple',
    steps: [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950],
  },
  {
    name: 'Gold',
    prefix: 'gold',
    description: 'Accent gold — Prestige and ownership highlights',
    steps: [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950],
  },
  {
    name: 'Success',
    prefix: 'success',
    description: 'Positive actions and confirmations',
    steps: [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950],
  },
  {
    name: 'Warning',
    prefix: 'warning',
    description: 'Caution states and attention-needed items',
    steps: [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950],
  },
  {
    name: 'Info',
    prefix: 'info',
    description: 'Informational elements and neutral highlights',
    steps: [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950],
  },
  {
    name: 'Danger',
    prefix: 'danger',
    description: 'Destructive actions and error states',
    steps: [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950],
  },
  {
    name: 'Surface',
    prefix: 'surface',
    description: 'Neutral surfaces and backgrounds with subtle hue',
    steps: [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950],
  },
];

const mixedColors = [
  { name: 'brand-muted', description: 'Muted brand for subtle backgrounds' },
  { name: 'brand-vivid', description: 'Vivid brand for emphasis' },
  { name: 'gold-soft', description: 'Softened gold for light backgrounds' },
  { name: 'gold-deep', description: 'Deepened gold for dark contexts' },
  { name: 'success-muted', description: 'Gentle success background' },
  { name: 'danger-muted', description: 'Gentle danger background' },
  { name: 'warning-muted', description: 'Gentle warning background' },
  { name: 'info-muted', description: 'Gentle info background' },
];

const socialColors = [
  { name: 'social-spotify', label: 'Spotify' },
  { name: 'social-youtube', label: 'YouTube' },
  { name: 'social-tiktok', label: 'TikTok' },
  { name: 'social-instagram', label: 'Instagram' },
  { name: 'social-twitter', label: 'Twitter/X' },
  { name: 'social-facebook', label: 'Facebook' },
  { name: 'social-soundcloud', label: 'SoundCloud' },
  { name: 'social-apple-music', label: 'Apple Music' },
];

const chartColors = [
  { name: 'chart-oklch-1', label: 'Chart 1' },
  { name: 'chart-oklch-2', label: 'Chart 2' },
  { name: 'chart-oklch-3', label: 'Chart 3' },
  { name: 'chart-oklch-4', label: 'Chart 4' },
  { name: 'chart-oklch-5', label: 'Chart 5' },
  { name: 'chart-oklch-6', label: 'Chart 6' },
];

function ColorSwatch({ colorClass, label, size = 'md' }) {
  const [copied, setCopied] = useState(false);
  const sizeMap = { sm: 'w-12 h-12', md: 'w-16 h-16', lg: 'w-20 h-20' };

  const handleCopy = () => {
    navigator.clipboard.writeText(colorClass);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  return (
    <button
      onClick={handleCopy}
      data-testid={`swatch-${colorClass}`}
      className="flex flex-col items-center gap-1 group cursor-pointer"
      title={`Click to copy: ${colorClass}`}
    >
      <div
        className={`${sizeMap[size]} rounded-lg border border-white/10 shadow-sm transition-transform duration-200 group-hover:scale-110 group-hover:shadow-md`}
        style={{ backgroundColor: `var(--color-${colorClass})` }}
      />
      <span className="text-xs text-surface-400 group-hover:text-surface-200 font-mono transition-colors">
        {copied ? 'Copied!' : label || colorClass}
      </span>
    </button>
  );
}

function ScaleRow({ scale }) {
  return (
    <div data-testid={`scale-${scale.prefix}`} className="mb-10">
      <div className="mb-3">
        <h3 className="text-lg font-semibold text-surface-100">{scale.name}</h3>
        <p className="text-sm text-surface-400">{scale.description}</p>
      </div>
      <div className="flex flex-wrap gap-3">
        {scale.steps.map((step) => (
          <ColorSwatch
            key={step}
            colorClass={`${scale.prefix}-${step}`}
            label={String(step)}
          />
        ))}
      </div>
    </div>
  );
}

export default function ColorSystemPage() {
  return (
    <div
      data-testid="color-system-page"
      className="min-h-screen p-6 sm:p-10"
      style={{ backgroundColor: 'var(--color-surface-950)' }}
    >
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <Link
            to="/"
            data-testid="back-to-home"
            className="inline-flex items-center gap-1 text-sm text-brand-400 hover:text-brand-300 mb-6 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
            Back to Home
          </Link>
          <h1 className="text-4xl sm:text-5xl font-bold text-surface-50 mb-2">
            Color System
          </h1>
          <p className="text-surface-400 text-base sm:text-lg max-w-2xl">
            OKLCH-powered color palette with <code className="text-brand-400 bg-surface-800 px-1.5 py-0.5 rounded text-sm">color-mix()</code> derived utilities. 
            Built for Vite 8 + Tailwind CSS v4 + Lightning CSS.
          </p>
        </div>

        {/* Usage Guide */}
        <section data-testid="usage-guide" className="mb-14 p-6 rounded-xl border border-surface-800" style={{ backgroundColor: 'var(--color-surface-900)' }}>
          <h2 className="text-xl font-semibold text-surface-100 mb-4">Usage in Tailwind</h2>
          <div className="grid sm:grid-cols-2 gap-4 text-sm font-mono">
            <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--color-surface-800)' }}>
              <span className="text-surface-400">Background:</span>
              <span className="text-brand-300 ml-2">bg-brand-500</span>
            </div>
            <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--color-surface-800)' }}>
              <span className="text-surface-400">Text:</span>
              <span className="text-gold-400 ml-2">text-gold-400</span>
            </div>
            <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--color-surface-800)' }}>
              <span className="text-surface-400">Border:</span>
              <span className="text-success-400 ml-2">border-success-600</span>
            </div>
            <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--color-surface-800)' }}>
              <span className="text-surface-400">Mixed:</span>
              <span className="text-info-300 ml-2">bg-brand-muted</span>
            </div>
          </div>
        </section>

        {/* OKLCH Scales */}
        <section data-testid="oklch-scales" className="mb-14">
          <h2 className="text-2xl font-bold text-surface-100 mb-6">OKLCH Color Scales</h2>
          {colorScales.map((scale) => (
            <ScaleRow key={scale.prefix} scale={scale} />
          ))}
        </section>

        {/* color-mix() Derived */}
        <section data-testid="color-mix-section" className="mb-14">
          <h2 className="text-2xl font-bold text-surface-100 mb-2">
            color-mix() Derived Colors
          </h2>
          <p className="text-sm text-surface-400 mb-6">
            Generated via <code className="text-brand-400 bg-surface-800 px-1.5 py-0.5 rounded text-sm">color-mix(in oklch, ...)</code> for perceptually uniform blending.
          </p>
          <div className="flex flex-wrap gap-4">
            {mixedColors.map((c) => (
              <ColorSwatch key={c.name} colorClass={c.name} label={c.name} size="lg" />
            ))}
          </div>
        </section>

        {/* Social Platform Colors */}
        <section data-testid="social-colors" className="mb-14">
          <h2 className="text-2xl font-bold text-surface-100 mb-6">Social Platform Colors</h2>
          <div className="flex flex-wrap gap-4">
            {socialColors.map((c) => (
              <ColorSwatch key={c.name} colorClass={c.name} label={c.label} size="lg" />
            ))}
          </div>
        </section>

        {/* Chart Palette */}
        <section data-testid="chart-palette" className="mb-14">
          <h2 className="text-2xl font-bold text-surface-100 mb-2">Chart Palette (Perceptually Uniform)</h2>
          <p className="text-sm text-surface-400 mb-6">
            OKLCH-based chart colors ensure equal visual weight across data series.
          </p>
          <div className="flex flex-wrap gap-4">
            {chartColors.map((c) => (
              <ColorSwatch key={c.name} colorClass={c.name} label={c.label} size="lg" />
            ))}
          </div>
        </section>

        {/* Live Preview Panels */}
        <section data-testid="live-preview" className="mb-14">
          <h2 className="text-2xl font-bold text-surface-100 mb-6">Live Preview</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {/* Card: Brand */}
            <div className="rounded-xl p-5 border border-brand-700" style={{ backgroundColor: 'var(--color-brand-900)' }}>
              <h3 className="font-semibold text-brand-200 mb-2">Brand Card</h3>
              <p className="text-sm text-brand-300">Uses brand-900 bg, brand-700 border, brand-200/300 text.</p>
              <button
                data-testid="preview-brand-btn"
                className="mt-3 px-4 py-1.5 rounded-full text-sm font-medium bg-brand-500 text-white hover:bg-brand-400 transition-colors"
              >
                Action
              </button>
            </div>
            {/* Card: Gold */}
            <div className="rounded-xl p-5 border border-gold-600" style={{ backgroundColor: 'var(--color-gold-900)' }}>
              <h3 className="font-semibold text-gold-200 mb-2">Gold Accent Card</h3>
              <p className="text-sm text-gold-300">Premium ownership highlights using the gold scale.</p>
              <span className="inline-block mt-3 px-3 py-1 rounded-full text-xs font-bold bg-gold-500 text-gold-950">
                OWNER
              </span>
            </div>
            {/* Card: Status */}
            <div className="rounded-xl p-5 border border-surface-700" style={{ backgroundColor: 'var(--color-surface-900)' }}>
              <h3 className="font-semibold text-surface-100 mb-3">Status Badges</h3>
              <div className="flex flex-wrap gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-500 text-white">Active</span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning-500 text-white">Pending</span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-danger-500 text-white">Expired</span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-info-500 text-white">Draft</span>
              </div>
            </div>
          </div>
        </section>

        {/* Technical Info */}
        <section data-testid="tech-info" className="mb-10 p-6 rounded-xl border border-surface-800" style={{ backgroundColor: 'var(--color-surface-900)' }}>
          <h2 className="text-xl font-semibold text-surface-100 mb-4">Technical Details</h2>
          <ul className="space-y-2 text-sm text-surface-300">
            <li><strong className="text-surface-100">Color Space:</strong> OKLCH (Oklab Lightness Chroma Hue) — perceptually uniform</li>
            <li><strong className="text-surface-100">CSS Functions:</strong> <code className="bg-surface-800 px-1 rounded">oklch()</code> + <code className="bg-surface-800 px-1 rounded">color-mix(in oklch, ...)</code></li>
            <li><strong className="text-surface-100">Build Pipeline:</strong> Vite 8 → Lightning CSS (default minifier) → modern browser targets</li>
            <li><strong className="text-surface-100">Browser Support:</strong> Chrome 111+, Edge 111+, Firefox 114+, Safari 16.4+</li>
            <li><strong className="text-surface-100">Terminal Colors:</strong> Use <code className="bg-surface-800 px-1 rounded">yarn start:no-color</code> or <code className="bg-surface-800 px-1 rounded">NO_COLOR=1</code> env var to disable ANSI output</li>
          </ul>
        </section>
      </div>
    </div>
  );
}
