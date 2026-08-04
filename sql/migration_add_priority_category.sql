-- Migration: Add priority and category to tickets table
-- Run this on your existing database to add the new columns

ALTER TABLE tickets 
ADD COLUMN IF NOT EXISTS priority TEXT DEFAULT 'medium';

ALTER TABLE tickets 
ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'general';

-- Update existing tickets with default values
UPDATE tickets 
SET priority = 'medium' 
WHERE priority IS NULL;

UPDATE tickets 
SET category = 'general' 
WHERE category IS NULL;
