
-- Stocks --
delete from stock_move;
delete from stock_quant;
delete from stock_production_lot;
delete from stock_inventory;


-- Factures --
delete from account_invoice;


-- Livraisons --
delete from stock_pack_operation;
delete from stock_picking;


-- Compta --
delete from account_payment;
delete from account_partial_reconcile;
delete from account_move;
delete from account_move_line;


-- Commandes --
delete from sale_order;


-- Commandes Fournisseur --
delete from purchase_order;

-- Commandes du POS --
delete from pos_order;
delete from pos_session;
delete from is_journal_des_ventes;

