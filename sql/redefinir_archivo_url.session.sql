-- @block edictos
SELECT COUNT(*) FROM `edictos` WHERE `url` IS NULL;

-- @block edictos update alter
UPDATE `edictos` SET `archivo` = '' WHERE `archivo` is NULL;
UPDATE `edictos` SET `url` = '' WHERE `url` is NULL;
ALTER TABLE `edictos` MODIFY `archivo` varchar(256) NOT NULL DEFAULT '';
ALTER TABLE `edictos` MODIFY `url` varchar(512) NOT NULL DEFAULT '';

-- @block glosas
SELECT COUNT(*) FROM `glosas` WHERE `url` IS NULL;

-- @block glosas update alter
UPDATE `glosas` SET `archivo` = '' WHERE `archivo` is NULL;
UPDATE `glosas` SET `url` = '' WHERE `url` is NULL;
ALTER TABLE `glosas` MODIFY `archivo` varchar(256) NOT NULL DEFAULT '';
ALTER TABLE `glosas` MODIFY `url` varchar(512) NOT NULL DEFAULT '';

-- @block listas_de_acuerdos
SELECT COUNT(*) FROM `listas_de_acuerdos` WHERE `url` IS NULL;

-- @block listas_de_acuerdos update alter
UPDATE `listas_de_acuerdos` SET `archivo` = '' WHERE `archivo` is NULL;
UPDATE `listas_de_acuerdos` SET `url` = '' WHERE `url` is NULL;
ALTER TABLE `listas_de_acuerdos` MODIFY `archivo` varchar(256) NOT NULL DEFAULT '';
ALTER TABLE `listas_de_acuerdos` MODIFY `url` varchar(512) NOT NULL DEFAULT '';

-- @block sentencias
SELECT COUNT(*) FROM `sentencias` WHERE `url` IS NULL;

-- @block sentencias nulos a texto vacio
UPDATE `sentencias` SET `archivo` = '' WHERE `archivo` is NULL;
UPDATE `sentencias` SET `url` = '' WHERE `url` is NULL;
ALTER TABLE `sentencias` MODIFY `archivo` varchar(256) NOT NULL DEFAULT '';
ALTER TABLE `sentencias` MODIFY `url` varchar(512) NOT NULL DEFAULT '';
