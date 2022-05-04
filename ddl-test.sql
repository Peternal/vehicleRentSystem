-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE TABLE ltd_corp_coupon (
    c_discount_rate DECIMAL(30, 2) NOT NULL COMMENT 'the rate of the discount',
    corp_coupon_id  DOUBLE NOT NULL
);


ALTER TABLE ltd_corp_coupon ADD CONSTRAINT ltd_corp_coupon_pk PRIMARY KEY ( corp_coupon_id );

-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE TABLE ltd_corp_cus (
    email          VARCHAR(30) NOT NULL COMMENT 'email of the customer',
    corp_no        VARCHAR(30) NOT NULL COMMENT 'the cop registrartion number',
    emp_id         VARCHAR(30) NOT NULL COMMENT 'the employee id of the customer',
    corp_name      VARCHAR(30) NOT NULL COMMENT 'the name of the corp',
    corp_coupon_id DOUBLE NOT NULL
);


ALTER TABLE ltd_corp_cus ADD CONSTRAINT ltd_corp_cus_pk PRIMARY KEY ( email );

ALTER TABLE ltd_corp_cus ADD CONSTRAINT ltd_corp_cus_pkv1 UNIQUE ( corp_no,
                                                                   emp_id );

-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE TABLE ltd_customer (
    email         VARCHAR(30) NOT NULL COMMENT 'email of the customer',
    phone         BIGINT NOT NULL COMMENT 'phone number of the customer',
    street        VARCHAR(30) NOT NULL COMMENT 'the street name of the address',
    city          VARCHAR(30) NOT NULL COMMENT 'the city of the address',
    state         VARCHAR(30) NOT NULL COMMENT 'the state of the address',
    zip           DECIMAL(30) NOT NULL COMMENT 'the zip code of the address',
    customer_type VARCHAR(1) NOT NULL COMMENT 'the type of the customer'
);

ALTER TABLE ltd_customer
    ADD CONSTRAINT ch_inh_ltd_customer CHECK ( customer_type IN ( 'c', 'i' ) );



ALTER TABLE ltd_customer ADD CONSTRAINT ltd_customer_pk PRIMARY KEY ( email );

-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE TABLE ltd_indi_coupon (
    indi_coupon_id     BIGINT NOT NULL COMMENT 'the coupon id ',
    indi_discount_rate DECIMAL(10, 2) NOT NULL COMMENT 'the rate of the discount',
    start_date         DATETIME NOT NULL COMMENT 'the start date',
    end_date           DATETIME NOT NULL COMMENT 'the end date of the coupon',
    license_id         VARCHAR(30)
);



ALTER TABLE ltd_indi_coupon ADD CONSTRAINT ltd_indi_coupon_pk PRIMARY KEY ( indi_coupon_id );

-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE TABLE ltd_indi_cus (
    email          VARCHAR(30) NOT NULL COMMENT 'email of the customer',
    license_id     VARCHAR(30) NOT NULL COMMENT 'the driver license number',
    cus_fn         VARCHAR(30) NOT NULL COMMENT 'the first name of the customer',
    cus_ln         VARCHAR(30) NOT NULL COMMENT 'the last name of the customer',
    insurance_name VARCHAR(30) NOT NULL COMMENT 'the insurance company name',
    insurance_no   VARCHAR(30) NOT NULL COMMENT 'the insrance number'
);


ALTER TABLE ltd_indi_cus ADD CONSTRAINT ltd_indi_cus_pk PRIMARY KEY ( email );

ALTER TABLE ltd_indi_cus ADD CONSTRAINT ltd_indi_cus_pkv1 UNIQUE ( license_id );

-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE TABLE ltd_invoice (
    invoice_id BIGINT NOT NULL AUTO_INCREMENT COMMENT 'the invoice id',
    `date`     DATETIME NOT NULL COMMENT 'the invoice date',
    amount     DECIMAL(30, 3) NOT NULL COMMENT 'the amount of this invoice',
    record_id  BIGINT NOT NULL,
    PRIMARY KEY  (`invoice_id`)
);



-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE UNIQUE INDEX ltd_invoice__idx ON
    ltd_invoice (
        record_id
    ASC );

-- ALTER TABLE ltd_invoice ADD CONSTRAINT ltd_invoice_pk PRIMARY KEY ( invoice_id );

-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE TABLE ltd_payment (
    payment_id     BIGINT NOT NULL AUTO_INCREMENT COMMENT 'the payment id',
    payment_date   DATETIME NOT NULL COMMENT 'the date of this payment',
    payment_status VARCHAR(30) NOT NULL COMMENT 'the status of this payment',
    payment_type   VARCHAR(30) NOT NULL COMMENT 'the payment type ( credit, debit, gift ) ',
    card_no        VARCHAR(30) NOT NULL COMMENT 'the card number ',
    invoice_id     BIGINT NOT NULL,
    PRIMARY KEY (`payment_id`)
);



-- ALTER TABLE ltd_payment ADD CONSTRAINT ltd_payment_pk PRIMARY KEY ( payment_id );

-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE TABLE ltd_rent_record (
    record_id         BIGINT NOT NULL AUTO_INCREMENT COMMENT 'the id of the record',
    pickup_office_id  VARCHAR(30) NOT NULL COMMENT 'the pick up location',
    dropoff_office_id VARCHAR(30) NOT NULL COMMENT 'the drop off location',
    pickup_date       DATETIME NOT NULL COMMENT 'the pick up date',
    dropoff_date      DATETIME NOT NULL COMMENT 'the drop off date',
    start_meter       DECIMAL(30) NOT NULL COMMENT 'the start millage',
    end_meter         DECIMAL(30) NOT NULL COMMENT 'the end millage',
    daliy_meter_limit DECIMAL(30) NOT NULL COMMENT 'the daily millage limit( if -1 then it''s unlimited)',
    email             VARCHAR(30) NOT NULL,
    vin               VARCHAR(30) NOT NULL,
    PRIMARY KEY (`record_id`)
);



-- ALTER TABLE ltd_rent_record ADD CONSTRAINT ltd_rent_record_pk PRIMARY KEY ( record_id );

-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE TABLE ltd_vehicle (
    vin                  VARCHAR(30) NOT NULL COMMENT 'the vin number of this vehicle',
    make                 VARCHAR(30) NOT NULL COMMENT 'the make of this vehicle',
    model                VARCHAR(30) NOT NULL COMMENT 'the model of this vehicle',
    year                 BIGINT NOT NULL COMMENT 'the year of this vehicle',
    license_plate_number VARCHAR(30) NOT NULL COMMENT 'the license plate number',
    status               DOUBLE NOT NULL COMMENT 'the renting status of this vehicle',
    class_name           VARCHAR(30) NOT NULL,
    office_id            VARCHAR(30)
);



ALTER TABLE ltd_vehicle ADD CONSTRAINT ltd_vehicle_pk PRIMARY KEY ( vin );

-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE TABLE ltd_vehicle_class (
    class_name       VARCHAR(30) NOT NULL COMMENT 'the class name',
    rental_rate      DECIMAL(10, 2) NOT NULL COMMENT 'rental rate',
    over_millage_fee DECIMAL(10, 2) NOT NULL COMMENT 'the over millage fee'
);



ALTER TABLE ltd_vehicle_class ADD CONSTRAINT ltd_vehicle_class_pk PRIMARY KEY ( class_name );

-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE TABLE ltd_wow_office (
    office_id   VARCHAR(30) NOT NULL COMMENT 'the office id ',
    office_name VARCHAR(30) NOT NULL COMMENT 'the name of this office',
    phone       VARCHAR(30) NOT NULL COMMENT 'the phone number of this office',
    street      VARCHAR(30) NOT NULL COMMENT 'the street of this office',
    city        VARCHAR(30) NOT NULL COMMENT 'the city of this office',
    state       VARCHAR(30) NOT NULL COMMENT 'the state of this office',
    zip         DECIMAL(30) NOT NULL COMMENT 'the zip code of this office'
);



ALTER TABLE ltd_wow_office ADD CONSTRAINT ltd_wow_office_pk PRIMARY KEY ( office_id );

ALTER TABLE ltd_corp_cus
    ADD CONSTRAINT corp_cus_corp_coupon_fk FOREIGN KEY ( corp_coupon_id )
        REFERENCES ltd_corp_coupon ( corp_coupon_id );

ALTER TABLE ltd_corp_cus
    ADD CONSTRAINT corp_cus_customer_fk FOREIGN KEY ( email )
        REFERENCES ltd_customer ( email );

ALTER TABLE ltd_indi_coupon
    ADD CONSTRAINT indi_coupon_indi_cus_fk FOREIGN KEY ( license_id )
        REFERENCES ltd_indi_cus ( license_id );

ALTER TABLE ltd_indi_cus
    ADD CONSTRAINT indi_cus_customer_fk FOREIGN KEY ( email )
        REFERENCES ltd_customer ( email );

ALTER TABLE ltd_invoice
    ADD CONSTRAINT invoice_rent_record_fk FOREIGN KEY ( record_id )
        REFERENCES ltd_rent_record ( record_id );

ALTER TABLE ltd_payment
    ADD CONSTRAINT payment_invoice_fk FOREIGN KEY ( invoice_id )
        REFERENCES ltd_invoice ( invoice_id );

ALTER TABLE ltd_rent_record
    ADD CONSTRAINT rent_record_customer_fk FOREIGN KEY ( email )
        REFERENCES ltd_customer ( email );

ALTER TABLE ltd_rent_record
    ADD CONSTRAINT rent_record_vehicle_fk FOREIGN KEY ( vin )
        REFERENCES ltd_vehicle ( vin );

ALTER TABLE ltd_rent_record 
	ADD CONSTRAINT dropoff_date CHECK (dropoff_date>=pickup_date);

-- CASCADE UPDATE ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
ALTER TABLE ltd_vehicle
    ADD CONSTRAINT vehicle_vehicle_class_fk FOREIGN KEY ( class_name )
        REFERENCES ltd_vehicle_class ( class_name ) ON UPDATE CASCADE;

ALTER TABLE ltd_vehicle
    ADD CONSTRAINT vehicle_wow_office_fk FOREIGN KEY ( office_id )
        REFERENCES ltd_wow_office ( office_id );

DELIMITER $$
    CREATE TRIGGER arc_fkarc_1_ltd_corp_cus BEFORE 
        INSERT ON ltd_corp_cus
        FOR EACH ROW
    BEGIN
    SET @d = (SELECT ltd_customer.customer_type FROM ltd_customer WHERE ltd_customer.email = new.email);
        IF  (@d IS NULL OR @d <> 'c') THEN
            signal sqlstate '72000' set message_text = 'FK corp_cus_customer_FK in Table ltd_corp_cus violates Arc constraint on Table ltd_customer - discriminator column customer_type doesn''t have value ''c''';
        END IF;
        
 END$$ 
DELIMITER ;

DELIMITER $$
    CREATE TRIGGER arc_fkarc_1_ltd_indi_cus BEFORE 
        INSERT ON ltd_indi_cus
        FOR EACH ROW
    BEGIN
    SET @d = (SELECT ltd_customer.customer_type FROM ltd_customer WHERE ltd_customer.email = new.email);
        IF  (@d IS NULL OR @d <> 'i') THEN
            signal sqlstate '72000' set message_text = 'FK corp_cus_customer_FK in Table ltd_corp_cus violates Arc constraint on Table ltd_customer - discriminator column customer_type doesn''t have value ''i''';
        END IF;
        
 END$$ 
DELIMITER ;


-- trigger to create invoice
delimiter |;
CREATE TRIGGER invoice_trigger
AFTER INSERT ON ltd_rent_record 
FOR EACH ROW
BEGIN 
 DECLARE extramile INT;
    DECLARE days INT;
    DECLARE discount INT;
    DECLARE IndiOrCorp CHAR;
    DECLARE amount INT;
    DECLARE overamount INT;
    
    SET extramile = new.daliy_meter_limit - (new.end_meter - new.start_meter);
 SET days = DATEDIFF(new.dropoff_date, new.pickup_date);

 SET IndiOrCorp = 
    (SELECT ltd_customer.customer_type
 FROM ltd_customer
 WHERE ltd_customer.email = new.email);
    
 IF IndiOrCorp = 'i' THEN
  SET discount = 
     (SELECT MIN(ltd_indi_coupon.indi_discount_rate)
     FROM ltd_indi_cus
     INNER JOIN ltd_indi_coupon
     ON ltd_indi_coupon.license_id = ltd_indi_cus.license_id and new.email = ltd_indi_cus.email);
 ELSE
  SET discount = 
  (SELECT MIN(ltd_corp_coupon.c_discount_rate)
  FROM ltd_corp_coupon
  INNER JOIN ltd_corp_cus
  ON ltd_corp_cus.corp_coupon_id = ltd_corp_coupon.corp_coupon_id and new.email = ltd_corp_cus.email);
 END IF;
    
    SET amount = 
 (SELECT SUM(ltd_vehicle_class.rental_rate * days * discount)
 FROM ltd_vehicle_class
 INNER JOIN ltd_vehicle
 ON ltd_vehicle.class_name = ltd_vehicle_class.class_name
 WHERE new.vin = ltd_vehicle.vin);
 

 SET overamount = 
 (SELECT SUM((ltd_vehicle_class.rental_rate * days + (-1 * extramile * ltd_vehicle_class.over_millage_fee)) * discount)
 FROM ltd_vehicle_class
 INNER JOIN ltd_vehicle
 ON ltd_vehicle.class_name = ltd_vehicle_class.class_name
 WHERE new.vin = ltd_vehicle.vin);


 IF new.daliy_meter_limit = -1 or extramile > 0 THEN
     INSERT INTO ltd_invoice VALUES(default, new.dropoff_date, amount, new.record_id);
    ELSEIF extramile < 0 THEN
        INSERT INTO ltd_invoice VALUES(default, new.dropoff_date, overamount, new.record_id);
 END IF;

END;
