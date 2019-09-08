-- Recreate everything
DELETE FROM promos WHERE 1;
DELETE FROM member_login WHERE 1;
DELETE FROM member_event WHERE 1;
DELETE FROM members WHERE 1;
DELETE FROM events WHERE 1;

ALTER TABLE promos AUTO_INCREMENT = 1;
ALTER TABLE members AUTO_INCREMENT = 1;
ALTER TABLE events AUTO_INCREMENT = 1;

-- Just reset essentials
DELETE FROM member_event WHERE MemberID > 0;

DELETE FROM members WHERE MemberID > 0;
ALTER TABLE members AUTO_INCREMENT = 1;

DELETE FROM events WHERE EventID > 0;
ALTER TABLE events AUTO_INCREMENT = 1;