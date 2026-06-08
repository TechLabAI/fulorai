import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WrksDataAccessComponent } from './wrks-data-access.component';

describe('WrksDataAccessComponent', () => {
  let component: WrksDataAccessComponent;
  let fixture: ComponentFixture<WrksDataAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WrksDataAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WrksDataAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
