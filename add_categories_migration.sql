-- Migration script to add categories system
-- Run this script in your MySQL database

-- 1. Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Create junction table for expert-categories relationship
CREATE TABLE IF NOT EXISTS expert_categories (
    expert_id INT NOT NULL,
    category_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (expert_id, category_id),
    FOREIGN KEY (expert_id) REFERENCES experts(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- 3. Insert default categories
INSERT INTO categories (name, description) VALUES
('Business Development', 'Business strategy, growth, and development consulting'),
('Marketing & Sales', 'Digital marketing, sales strategies, and customer acquisition'),
('Finance & Accounting', 'Financial planning, accounting, and investment advice'),
('Technology & IT', 'Software development, IT consulting, and digital transformation'),
('Operations & Management', 'Process optimization, team management, and operations'),
('Legal & Compliance', 'Legal advice, compliance, and regulatory matters'),
('Human Resources', 'HR management, recruitment, and talent development'),
('Consulting', 'General business consulting and advisory services'),
('Data Science & Analytics', 'Data analysis, machine learning, and business intelligence'),
('Digital Marketing', 'Social media, SEO, content marketing, and online advertising'),
('Product Management', 'Product strategy, development, and lifecycle management'),
('Design & Creative', 'UI/UX design, graphic design, and creative solutions');

-- 4. Optional: Migrate existing expertise data to categories
-- This will create categories from existing expertise fields and assign them to experts
-- Uncomment the following lines if you want to auto-migrate existing data:

/*
-- Create categories from existing expertise (if not already exists)
INSERT IGNORE INTO categories (name, description)
SELECT DISTINCT 
    TRIM(expertise) as name, 
    CONCAT('Expertise in ', TRIM(expertise)) as description
FROM experts 
WHERE expertise IS NOT NULL 
  AND TRIM(expertise) != '' 
  AND TRIM(expertise) NOT IN (SELECT name FROM categories);

-- Assign existing experts to their corresponding categories
INSERT IGNORE INTO expert_categories (expert_id, category_id)
SELECT DISTINCT e.id, c.id
FROM experts e
JOIN categories c ON TRIM(e.expertise) = c.name
WHERE e.expertise IS NOT NULL AND TRIM(e.expertise) != '';
*/

-- 5. Verification queries (run these to check the migration)
-- SELECT COUNT(*) as category_count FROM categories;
-- SELECT COUNT(*) as expert_category_relationships FROM expert_categories;
-- SELECT c.name, COUNT(ec.expert_id) as expert_count FROM categories c LEFT JOIN expert_categories ec ON c.id = ec.category_id GROUP BY c.id, c.name;
