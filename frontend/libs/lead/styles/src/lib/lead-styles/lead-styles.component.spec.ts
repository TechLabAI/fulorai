import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadStylesComponent } from './lead-styles.component';

describe('LeadStylesComponent', () => {
  let component: LeadStylesComponent;
  let fixture: ComponentFixture<LeadStylesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadStylesComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadStylesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
