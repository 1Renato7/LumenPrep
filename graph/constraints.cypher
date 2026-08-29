// CTR-MEM-001 graph model. All merges use stable IDs for replay-safe seeding.
CREATE CONSTRAINT incident_id IF NOT EXISTS FOR (node:Incident) REQUIRE node.incident_id IS UNIQUE;
CREATE CONSTRAINT evidence_id IF NOT EXISTS FOR (node:Evidence) REQUIRE node.evidence_id IS UNIQUE;
CREATE CONSTRAINT playbook_id IF NOT EXISTS FOR (node:Playbook) REQUIRE node.playbook_id IS UNIQUE;
CREATE CONSTRAINT cause_id IF NOT EXISTS FOR (node:Cause) REQUIRE node.cause_id IS UNIQUE;
CREATE CONSTRAINT provider_id IF NOT EXISTS FOR (node:Provider) REQUIRE node.provider_id IS UNIQUE;
CREATE CONSTRAINT country_code IF NOT EXISTS FOR (node:Country) REQUIRE node.code IS UNIQUE;
CREATE CONSTRAINT brand_name IF NOT EXISTS FOR (node:CardBrand) REQUIRE node.name IS UNIQUE;

