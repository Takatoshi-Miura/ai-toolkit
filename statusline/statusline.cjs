#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Constants
const COMPACTION_THRESHOLD = 200000 * 0.8

// Read JSON from stdin
let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', async () => {
  try {
    const data = JSON.parse(input);

    // Extract values
    const model = data.model?.display_name || 'Unknown';
    const currentDir = path.basename(data.workspace?.current_dir || data.cwd || '.');
    const sessionId = data.session_id;

    // Calculate token usage for current session
    let totalTokens = 0;

    if (sessionId) {
      // Find all transcript files
      const projectsDir = path.join(process.env.HOME, '.claude', 'projects');

      if (fs.existsSync(projectsDir)) {
        // Get all project directories
        const projectDirs = fs.readdirSync(projectsDir)
          .map(dir => path.join(projectsDir, dir))
          .filter(dir => fs.statSync(dir).isDirectory());

        // Search for the current session's transcript file
        for (const projectDir of projectDirs) {
          const transcriptFile = path.join(projectDir, `${sessionId}.jsonl`);

          if (fs.existsSync(transcriptFile)) {
            totalTokens = await calculateTokensFromTranscript(transcriptFile);
            break;
          }
        }
      }
    }

    // Calculate percentage
    const percentage = Math.min(100, Math.round((totalTokens / COMPACTION_THRESHOLD) * 100));

    // Format token display
    const tokenDisplay = formatTokenCount(totalTokens);

    // Color coding for percentage
    const percentageColor = getColorByPercentage(percentage);

    // Build rate limits display
    const rateLimitDisplay = formatRateLimits(data.rate_limits);

    // Build status line
    let statusLine = `[${model}] 📁 ${currentDir} | 🪙 ${tokenDisplay} | ${percentageColor}${percentage}%\x1b[0m`;
    if (rateLimitDisplay) {
      statusLine += ` | ${rateLimitDisplay}`;
    }

    console.log(statusLine);
  } catch (error) {
    // Fallback status line on error
    console.log('[Error] 📁 . | 🪙 0 | 0%');
  }
});

async function calculateTokensFromTranscript(filePath) {
  return new Promise((resolve, reject) => {
    let lastUsage = null;

    const fileStream = fs.createReadStream(filePath);
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });

    rl.on('line', (line) => {
      try {
        const entry = JSON.parse(line);

        // Check if this is an assistant message with usage data
        if (entry.type === 'assistant' && entry.message?.usage) {
          lastUsage = entry.message.usage;
        }
      } catch (e) {
        // Skip invalid JSON lines
      }
    });

    rl.on('close', () => {
      if (lastUsage) {
        // The last usage entry contains cumulative tokens
        const totalTokens = (lastUsage.input_tokens || 0) +
          (lastUsage.output_tokens || 0) +
          (lastUsage.cache_creation_input_tokens || 0) +
          (lastUsage.cache_read_input_tokens || 0);
        resolve(totalTokens);
      } else {
        resolve(0);
      }
    });

    rl.on('error', (err) => {
      reject(err);
    });
  });
}

function formatTokenCount(tokens) {
  if (tokens >= 1000000) {
    return `${(tokens / 1000000).toFixed(1)}M`;
  } else if (tokens >= 1000) {
    return `${(tokens / 1000).toFixed(1)}K`;
  }
  return tokens.toString();
}

function getColorByPercentage(percentage) {
  if (percentage >= 90) return '\x1b[31m'; // Red
  if (percentage >= 70) return '\x1b[33m'; // Yellow
  return '\x1b[32m'; // Green
}

function formatRateLimits(rateLimits) {
  if (!rateLimits) return '';

  const parts = [];

  const fiveHour = rateLimits.five_hour;
  if (fiveHour?.used_percentage != null) {
    const pct = Math.round(fiveHour.used_percentage);
    const color = getColorByPercentage(pct);
    const reset = fiveHour.resets_at ? `(${formatTime(fiveHour.resets_at)})` : '';
    parts.push(`5h: ${color}${pct}%\x1b[0m${reset}`);
  }

  const sevenDay = rateLimits.seven_day;
  if (sevenDay?.used_percentage != null) {
    const pct = Math.round(sevenDay.used_percentage);
    const color = getColorByPercentage(pct);
    const reset = sevenDay.resets_at ? `(${formatDate(sevenDay.resets_at)})` : '';
    parts.push(`7d: ${color}${pct}%\x1b[0m${reset}`);
  }

  return parts.length > 0 ? `⏱ ${parts.join(' ')}` : '';
}

function formatTime(unixTimestamp) {
  const date = new Date(unixTimestamp * 1000);
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
}

function formatDate(unixTimestamp) {
  const date = new Date(unixTimestamp * 1000);
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${month}/${day}`;
}
